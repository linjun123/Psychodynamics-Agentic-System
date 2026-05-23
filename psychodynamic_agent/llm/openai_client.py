import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel, ValidationError


class LLMOutputError(RuntimeError):
    pass


class OpenAIResponsesClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_json(
        self,
        *,
        model: str,
        system_prompt: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
    ) -> dict[str, Any]:
        resp = self.client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload)},
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema.__name__,
                    "schema": schema.model_json_schema(),
                    "strict": True,
                }
            },
        )
        status = getattr(resp, "status", None)
        if status in {"incomplete", "failed", "cancelled"}:
            raise LLMOutputError(f"Model returned non-complete response status: {status}")

        text = getattr(resp, "output_text", "")
        if not text:
            raise LLMOutputError("Model response did not include output_text")

        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            raise LLMOutputError("Model output_text was not valid JSON") from exc

        try:
            return schema.model_validate(parsed).model_dump()
        except ValidationError as exc:
            raise LLMOutputError("Model JSON did not match target schema") from exc


class MockLLMClient:
    def __init__(self, fixtures: dict[str, dict[str, Any]]):
        self.fixtures = fixtures

    def generate_json(
        self,
        *,
        model: str,
        system_prompt: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
    ) -> dict[str, Any]:
        del model, payload, schema
        for key, value in self.fixtures.items():
            if key in system_prompt:
                return value
        raise KeyError("No fixture for prompt")
