from psychodynamic_agent.agents.base import BaseLLMAgent
from psychodynamic_agent.prompts import SAFETY_GATE_SYSTEM_PROMPT
from psychodynamic_agent.schemas import SafetyGateOutput


class FinalSafetyGateAgent(BaseLLMAgent):
    def __init__(self, llm_client, model: str):
        super().__init__(
            llm_client=llm_client,
            model=model,
            system_prompt=SAFETY_GATE_SYSTEM_PROMPT,
            schema=SafetyGateOutput,
        )
