from psychodynamic_agent.schemas import CensorAOutput, EgoReport, IdOutput


def _assert_no_additional_properties(schema: dict):
    assert schema.get("additionalProperties") is False


def test_strict_schema_additional_properties_false_top_and_nested():
    for model in (IdOutput, CensorAOutput, EgoReport):
        schema = model.model_json_schema()
        _assert_no_additional_properties(schema)
        for value in schema.get("$defs", {}).values():
            if value.get("type") == "object":
                _assert_no_additional_properties(value)
