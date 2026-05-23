from psychodynamic_agent.schemas.state import FullInternalState, Message


def test_state_schema_validation():
    state = FullInternalState(user_input="hi", conversation_history=[Message(role="user", content="hi")])
    assert state.user_input == "hi"
