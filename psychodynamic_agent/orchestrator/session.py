from dataclasses import dataclass
from typing import Any

from psychodynamic_agent.config import Settings
from psychodynamic_agent.llm import OpenAIResponsesClient
from psychodynamic_agent.orchestrator.memory import InMemoryConversation
from psychodynamic_agent.orchestrator.pipeline import GuardMode, PsychodynamicPipeline


@dataclass(frozen=True)
class ChatTurnResult:
    final_response: str
    approved: bool
    raw: dict[str, Any]


class PsychodynamicChatSession:
    def __init__(
        self,
        *,
        llm_client: OpenAIResponsesClient,
        memory: InMemoryConversation,
        pipeline: PsychodynamicPipeline,
    ):
        self.llm_client = llm_client
        self.memory = memory
        self.pipeline = pipeline

    @classmethod
    def from_settings(
        cls,
        settings: Settings,
        u_star: str | None = None,
        *,
        guard_mode: GuardMode = "enforce",
    ) -> "PsychodynamicChatSession":
        llm = OpenAIResponsesClient(api_key=settings.openai_api_key)
        memory = InMemoryConversation()
        pipeline = cls._build_pipeline(
            llm_client=llm,
            settings=settings,
            u_star=u_star,
            guard_mode=guard_mode,
        )
        return cls(llm_client=llm, memory=memory, pipeline=pipeline)

    @staticmethod
    def _build_pipeline(
        *,
        llm_client: OpenAIResponsesClient,
        settings: Settings,
        u_star: str | None,
        guard_mode: GuardMode,
    ) -> PsychodynamicPipeline:
        return PsychodynamicPipeline(
            llm_client=llm_client,
            model_internal=settings.openai_model_internal,
            model_main=settings.openai_model_main,
            sealed_ultimate_need=u_star or settings.ultimate_need_seed,
            guard_mode=guard_mode,
        )

    def reset_pipeline_preserving_memory(
        self,
        settings: Settings,
        u_star: str | None = None,
        *,
        guard_mode: GuardMode = "enforce",
    ) -> None:
        """Replace the pipeline without changing recorded public conversation memory."""
        self.pipeline = self._build_pipeline(
            llm_client=self.llm_client,
            settings=settings,
            u_star=u_star,
            guard_mode=guard_mode,
        )

    def send(self, user_input: str, debug: bool = False) -> ChatTurnResult:
        state = self.memory.build_state(user_input)
        out = self.pipeline.run(state, debug=debug)
        final_response = str(out.get("final_response", ""))
        approved = bool(out.get("approved", False))
        self.memory.record_turn(user_input=user_input, final_response=final_response, out=out)
        return ChatTurnResult(final_response=final_response, approved=approved, raw=out)
