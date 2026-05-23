import json
from typing import Any

from openai import OpenAI
from pydantic import BaseModel


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
        schema_json = schema.model_json_schema()
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
                    "schema": schema_json,
                    "strict": True,
                }
            },
        )
        text = getattr(resp, "output_text", "")
        if not text:
            raise ValueError("No output_text from model")
        return json.loads(text)


class MockLLMClient:
    def __init__(self, fixtures: dict[str, dict[str, Any]]):
        self.fixtures = fixtures
        self.calls: list[dict[str, Any]] = []

    def generate_json(
        self,
        *,
        model: str,
        system_prompt: str,
        payload: dict[str, Any],
        schema: type[BaseModel],
    ) -> dict[str, Any]:
        self.calls.append(
            {
                "model": model,
                "system_prompt": system_prompt,
                "payload": payload,
                "schema": schema.__name__,
            }
        )
        for key, value in self.fixtures.items():
            if key in system_prompt:
                return value
        raise KeyError("No fixture for prompt")
