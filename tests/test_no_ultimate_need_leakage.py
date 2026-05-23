from psychodynamic_agent.agents.id_agent import IdAgent
from psychodynamic_agent.llm import MockLLMClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation


def test_id_agent_private_payload_contains_u_star_only_inside_id_agent():
    secret = "TOP_SECRET_USTAR"
    state = InMemoryConversation().build_state("hi")
    agent = IdAgent(llm_client=MockLLMClient({}), model="m", sealed_ultimate_need=secret)
    payload = agent.build_private_payload(state)
    assert payload["sealed_context"]["u_star"] == secret
    assert "u_star" not in payload["state"]
