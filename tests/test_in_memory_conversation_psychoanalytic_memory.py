from psychodynamic_agent.orchestrator.memory import InMemoryConversation


def test_in_memory_conversation_records_psychoanalytic_memory_without_debug() -> None:
    conversation = InMemoryConversation()

    conversation.record_turn("hello", "hi", out=None)

    assert [message.role for message in conversation.history] == ["user", "assistant"]
    assert conversation.previous_main_outputs == ["hi"]
    assert conversation.psychoanalytic_memory.trace_count() == 1


def test_in_memory_conversation_records_rich_trace_from_safe_debug() -> None:
    conversation = InMemoryConversation()

    conversation.record_turn(
        "I am curious and worried about being ignored.",
        "response",
        out={
            "safe_debug_trace": {
                "id_output": {
                    "raw_affect": {
                        "valence": -0.5,
                        "arousal": 0.8,
                        "fear_of_loss": 0.7,
                        "curiosity": 0.6,
                    }
                },
                "public_affect_dynamics": {"caution_level": "high"},
            }
        },
    )

    latest = conversation.psychoanalytic_memory.latest_trace()
    assert latest is not None
    assert latest.affective_signature.valence == 0.25
    assert latest.affective_signature.arousal == 0.8
    assert latest.affective_signature.fear_of_loss == 0.7
    assert latest.affective_signature.curiosity == 0.6


def test_in_memory_conversation_build_state_does_not_include_private_memory() -> None:
    conversation = InMemoryConversation()
    conversation.record_turn("I feel embarrassed", "response")

    state = conversation.build_state("next")
    serialized = state.model_dump_json()

    assert not hasattr(state, "psychoanalytic_memory")
    assert "private_core_summary" not in serialized
    assert "MemoryTrace" not in serialized


def test_existing_public_memory_recording_still_works() -> None:
    conversation = InMemoryConversation()
    safe_debug_trace = {
        "ego_report": {
            "summary": "public",
            "sealed_ultimate_need": "must not be copied",
        },
        "public_affect_dynamics": {
            "satisfaction": 0.4,
            "latent_alignment": "must not be copied",
        },
    }

    conversation.record_turn("hello", "hi", out={"safe_debug_trace": safe_debug_trace})

    assert conversation.previous_ego_reports == [{"summary": "public"}]
    assert conversation.satisfaction_history == [{"satisfaction": 0.4}]
    assert conversation.psychoanalytic_memory.trace_count() == 1
