import json
from typing import Any

from openai import OpenAI


class OpenAIResponsesClient:
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def generate_json(self, *, model: str, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
        resp = self.client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload)},
            ],
        )
        text = getattr(resp, "output_text", "")
        if not text:
            raise ValueError("No output_text from model")
        return json.loads(text)


class MockLLMClient:
    def __init__(self, fixtures: dict[str, dict[str, Any]]):
        self.fixtures = fixtures

    def generate_json(self, *, model: str, system_prompt: str, payload: dict[str, Any]) -> dict[str, Any]:
        for key, value in self.fixtures.items():
            if key in system_prompt:
                return value
        raise KeyError("No fixture for prompt")
