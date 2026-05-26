import json

from psychodynamic_agent.llm.openai_client import OpenAIResponsesClient
from psychodynamic_agent.llm.schema_sanitizer import (
    assert_no_ref_siblings,
    sanitize_schema_for_openai,
)
from psychodynamic_agent.schemas import (
    CensorAOutput,
    ConsciousEgoReport,
    EgoReport,
    IdOutput,
    MainAIOutput,
    PrivateIdTurnOutput,
    SafetyGateOutput,
)
from tests.test_id_private_turn_phase6a3 import private_id_turn_fixture


def test_sanitizer_removes_ref_sibling_description_and_keeps_defs() -> None:
    raw = {
        "type": "object",
        "properties": {
            "drive_state": {
                "$ref": "#/$defs/DriveState",
                "description": "bad sibling",
            }
        },
        "$defs": {
            "DriveState": {
                "type": "object",
                "properties": {
                    "pressure": {
                        "type": "number",
                        "description": "keep this",
                    }
                },
                "required": ["pressure"],
                "additionalProperties": False,
            }
        },
        "required": ["drive_state"],
        "additionalProperties": False,
    }

    sanitized = sanitize_schema_for_openai(raw)

    assert sanitized["properties"]["drive_state"] == {"$ref": "#/$defs/DriveState"}
    assert sanitized["$defs"]["DriveState"]["properties"]["pressure"]["description"] == "keep this"
    assert raw["properties"]["drive_state"]["description"] == "bad sibling"


def test_private_id_turn_schema_sanitization() -> None:
    raw = PrivateIdTurnOutput.model_json_schema()
    sanitized = sanitize_schema_for_openai(raw)

    assert_no_ref_siblings(sanitized)
    assert "$defs" in sanitized
    assert set(sanitized["required"]) >= {
        "id_output",
        "latent_alignment",
        "updated_affect_state",
        "public_affect_dynamics",
    }
    assert sanitized["additionalProperties"] is False


def test_all_llm_facing_schemas_have_no_ref_siblings_after_sanitize() -> None:
    for model in (
        PrivateIdTurnOutput,
        IdOutput,
        CensorAOutput,
        EgoReport,
        ConsciousEgoReport,
        MainAIOutput,
        SafetyGateOutput,
    ):
        sanitized = sanitize_schema_for_openai(model.model_json_schema())
        assert_no_ref_siblings(sanitized)


def test_openai_responses_client_passes_sanitized_schema() -> None:
    captured: dict = {}

    class FakeResponses:
        def create(self, **kwargs):
            captured.update(kwargs)
            return type(
                "Resp",
                (),
                {"status": "completed", "output_text": json.dumps(private_id_turn_fixture())},
            )()

    class FakeClient:
        responses = FakeResponses()

    client = OpenAIResponsesClient(api_key="dummy")
    client.client = FakeClient()

    result = client.generate_json(
        model="gpt-test",
        system_prompt="Id private-turn module",
        payload={"message": "hi"},
        schema=PrivateIdTurnOutput,
    )

    raw = PrivateIdTurnOutput.model_json_schema()
    sent_schema = captured["text"]["format"]["schema"]

    assert_no_ref_siblings(sent_schema)
    assert sent_schema is not raw
    assert result == PrivateIdTurnOutput.model_validate(private_id_turn_fixture()).model_dump()
