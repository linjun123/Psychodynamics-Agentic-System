from psychodynamic_agent.agents.base import BaseLLMAgent
from psychodynamic_agent.prompts import CENSOR_A_SYSTEM_PROMPT
from psychodynamic_agent.schemas import CensorAOutput


class CensorAAgent(BaseLLMAgent):
    def __init__(self, llm_client, model: str):
        super().__init__(
            llm_client=llm_client,
            model=model,
            system_prompt=CENSOR_A_SYSTEM_PROMPT,
            schema=CensorAOutput,
        )
