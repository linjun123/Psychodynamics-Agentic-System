from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class BaseLLMAgent:
    def __init__(self, *, llm_client: Any, model: str, system_prompt: str, schema: type[T]):
        self.llm_client = llm_client
        self.model = model
        self.system_prompt = system_prompt
        self.schema = schema

    def run(self, payload: dict[str, Any], retries: int = 2) -> T:
        last_error: Exception | None = None
        for _ in range(retries + 1):
            try:
                raw = self.llm_client.generate_json(
                    model=self.model, system_prompt=self.system_prompt, payload=payload
                )
                return self.schema.model_validate(raw)
            except (ValidationError, ValueError, KeyError) as exc:
                last_error = exc
        raise RuntimeError(f"Agent failed after retries: {last_error}")
