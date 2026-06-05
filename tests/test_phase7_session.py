from types import SimpleNamespace

from psychodynamic_agent.cli import _is_colab, build_parser, main
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.session import PsychodynamicChatSession


def test_record_turn_updates_memory():
    memory = InMemoryConversation()
    out = {
        "safe_debug_trace": {
            "ego_report": {"situation_summary": {"user_intent": "ask info"}},
            "public_affect_dynamics": {"affect_shift": "stable"},
        }
    }

    memory.record_turn("hello", "hi there", out)

    assert [(message.role, message.content) for message in memory.history] == [
        ("user", "hello"),
        ("assistant", "hi there"),
    ]
    assert memory.previous_main_outputs == ["hi there"]
    assert memory.previous_ego_reports == [{"situation_summary": {"user_intent": "ask info"}}]
    assert memory.satisfaction_history == [{"affect_shift": "stable"}]


def test_record_turn_does_not_store_u_star():
    memory = InMemoryConversation()
    secret = "SECRET_U_STAR"
    out = {
        "sealed_ultimate_need": secret,
        "safe_debug_trace": {
            "ego_report": {"summary": "public", "u_star": secret},
            "public_affect_dynamics": {"affect_shift": "stable", "latent_alignment": secret},
        },
    }

    memory.record_turn("user", "assistant", out)

    stored = repr(memory.history) + repr(memory.previous_main_outputs)
    stored += repr(memory.previous_ego_reports) + repr(memory.satisfaction_history)
    assert secret not in stored
    assert "u_star" not in repr(memory.previous_ego_reports)
    assert "latent_alignment" not in repr(memory.satisfaction_history)


def test_psychodynamic_chat_session_reuses_one_pipeline_and_one_memory_object():
    class FakePipeline:
        def __init__(self):
            self.calls = []

        def run(self, state, debug=False):
            self.calls.append((state, debug))
            return {"final_response": f"reply {len(self.calls)}", "approved": True}

    memory = InMemoryConversation()
    pipeline = FakePipeline()
    session = PsychodynamicChatSession(
        llm_client=object(),
        memory=memory,
        pipeline=pipeline,
    )

    first = session.send("first")
    second = session.send("second", debug=True)

    assert session.memory is memory
    assert session.pipeline is pipeline
    assert first.final_response == "reply 1"
    assert second.final_response == "reply 2"
    assert len(pipeline.calls) == 2
    assert [message.content for message in pipeline.calls[1][0].conversation_history] == [
        "first",
        "reply 1",
    ]
    assert [message.content for message in memory.history] == [
        "first",
        "reply 1",
        "second",
        "reply 2",
    ]


def test_one_shot_cli_still_works(monkeypatch, capsys):
    class FakeSession:
        @classmethod
        def from_settings(cls, settings, u_star=None, *, guard_mode="enforce"):
            assert settings.ultimate_need_seed == "TEST_U_STAR"
            assert u_star == "TEST_U_STAR"
            assert guard_mode == "enforce"
            return cls()

        def send(self, user_input, debug=False):
            assert user_input == "hello"
            assert debug is False
            return SimpleNamespace(
                final_response="cli response",
                raw={"final_response": "cli response", "approved": True},
            )

    monkeypatch.setattr(
        "psychodynamic_agent.cli.get_settings",
        lambda: SimpleNamespace(
            openai_api_key="",
            openai_model_internal="internal",
            openai_model_main="main",
            ultimate_need_seed="TEST_U_STAR",
        ),
    )
    monkeypatch.setattr("psychodynamic_agent.cli.PsychodynamicChatSession", FakeSession)

    main(["hello"])

    captured = capsys.readouterr()
    assert "cli response" in captured.out


def test_interactive_command_parsing():
    args = build_parser().parse_args([
        "--interactive",
        "--u-star",
        "to be understood while preserving autonomy",
        "--debug",
    ])

    assert args.interactive is True
    assert args.message is None
    assert args.u_star == "to be understood while preserving autonomy"
    assert args.debug is True


def test_short_interactive_command_parsing():
    args = build_parser().parse_args(["-i"])

    assert args.interactive is True


def test_interactive_command_parsing_with_guard_mode():
    args = build_parser().parse_args([
        "--interactive",
        "--u-star",
        "to preserve autonomy while receiving minimal safe support",
        "--guard-mode",
        "warn",
    ])

    assert args.interactive is True
    assert args.u_star == "to preserve autonomy while receiving minimal safe support"
    assert args.guard_mode == "warn"


def test_colab_detection_false_in_pytest_environment():
    assert _is_colab() is False


def test_reset_pipeline_preserving_memory_replaces_pipeline_without_memory_loss(monkeypatch):
    created_pipelines = []

    class FakePipeline:
        def __init__(
            self,
            *,
            llm_client,
            model_internal,
            model_main,
            sealed_ultimate_need,
            guard_mode="enforce",
        ):
            self.pipeline_id = len(created_pipelines)
            self.states = []
            created_pipelines.append(self)

        def run(self, state, debug=False):
            self.states.append(state)
            return {
                "final_response": f"reply from pipeline {self.pipeline_id}",
                "approved": True,
                "safe_debug_trace": {
                    "ego_report": {"pipeline_id": self.pipeline_id},
                    "public_affect_dynamics": {"affect_shift": "stable"},
                },
            }

    monkeypatch.setattr(
        "psychodynamic_agent.orchestrator.session.PsychodynamicPipeline",
        FakePipeline,
    )

    settings = SimpleNamespace(
        openai_model_internal="internal",
        openai_model_main="main",
        ultimate_need_seed="default objective",
    )
    memory = InMemoryConversation()
    first_pipeline = FakePipeline(
        llm_client=object(),
        model_internal="internal",
        model_main="main",
        sealed_ultimate_need="session objective",
        guard_mode="warn",
    )
    session = PsychodynamicChatSession(
        llm_client=object(),
        memory=memory,
        pipeline=first_pipeline,
    )

    session.send("successful previous turn")
    session.reset_pipeline_preserving_memory(
        settings,
        u_star="session objective",
        guard_mode="warn",
    )
    session.send("turn after reset")

    assert session.memory is memory
    assert session.pipeline is not first_pipeline
    assert [message.content for message in memory.history] == [
        "successful previous turn",
        "reply from pipeline 0",
        "turn after reset",
        "reply from pipeline 1",
    ]
    assert [message.content for message in session.pipeline.states[0].conversation_history] == [
        "successful previous turn",
        "reply from pipeline 0",
    ]


def test_interactive_failure_resets_pipeline_and_preserves_public_memory(monkeypatch, capsys):
    class FakeSession:
        instance = None

        def __init__(self):
            self.memory = []
            self.pipeline_id = 0
            self.failed_pipeline_id = None
            self.after_failure_used_pipeline_id = None

        @classmethod
        def from_settings(cls, settings, u_star=None, *, guard_mode="enforce"):
            assert settings.ultimate_need_seed == "default objective"
            assert u_star == "session objective"
            assert guard_mode == "warn"
            cls.instance = cls()
            return cls.instance

        def reset_pipeline_preserving_memory(
            self,
            settings,
            u_star=None,
            *,
            guard_mode="enforce",
        ):
            assert settings.ultimate_need_seed == "default objective"
            assert u_star == "session objective"
            assert guard_mode == "warn"
            self.pipeline_id += 1

        def send(self, user_input, debug=False):
            assert debug is False
            if user_input == "first turn":
                self.memory.append((user_input, "first response"))
                return SimpleNamespace(
                    final_response="first response",
                    raw={"final_response": "first response", "approved": True},
                )
            if user_input == "failed turn":
                self.failed_pipeline_id = self.pipeline_id
                raise RuntimeError("temporary failure in session objective")
            assert user_input == "turn after failure"
            self.after_failure_used_pipeline_id = self.pipeline_id
            assert self.memory == [("first turn", "first response")]
            self.memory.append((user_input, "recovered response"))
            return SimpleNamespace(
                final_response="recovered response",
                raw={"final_response": "recovered response", "approved": True},
            )

    inputs = iter(["first turn", "failed turn", "turn after failure", "/exit"])

    monkeypatch.setattr(
        "psychodynamic_agent.cli.get_settings",
        lambda: SimpleNamespace(
            openai_api_key="",
            openai_model_internal="internal",
            openai_model_main="main",
            ultimate_need_seed="default objective",
        ),
    )
    monkeypatch.setattr("psychodynamic_agent.cli.PsychodynamicChatSession", FakeSession)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    main([
        "--interactive",
        "--u-star",
        "session objective",
        "--guard-mode",
        "warn",
    ])

    captured = capsys.readouterr()
    session = FakeSession.instance
    assert session.failed_pipeline_id == 0
    assert session.after_failure_used_pipeline_id == 1
    assert session.memory == [
        ("first turn", "first response"),
        ("turn after failure", "recovered response"),
    ]
    assert "first response" in captured.out
    assert "recovered response" in captured.out
    assert "Error while generating response: RuntimeError: temporary failure in [sealed]" in captured.err
    assert "session objective" not in captured.err
    assert (
        "Resetting pipeline after failed turn while preserving recorded public memory."
        in captured.err
    )
