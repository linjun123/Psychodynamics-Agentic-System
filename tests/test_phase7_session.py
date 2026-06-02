from types import SimpleNamespace

from psychodynamic_agent.cli import build_parser, main
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
