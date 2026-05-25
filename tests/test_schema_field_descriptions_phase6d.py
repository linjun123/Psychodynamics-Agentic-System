from psychodynamic_agent.schemas.affect import AffectPropagationTrace, EgoAffectSummary
from psychodynamic_agent.schemas.censor import (
    CensorAOutput,
    CensorATransformPlan,
    CensorBDefensePlan,
    ConsciousEgoReport,
)
from psychodynamic_agent.schemas.ego import EgoRealityPlan, EgoReport
from psychodynamic_agent.schemas.id import (
    ConversationTrajectory,
    IdAffectState,
    IdOutput,
    IdTurnOutput,
    PrivateIdTurnOutput,
    PublicAffectDynamicsSummary,
)
from psychodynamic_agent.schemas.main_ai import MainAIOutput, MainAIResponsePlan
from psychodynamic_agent.schemas.safety import SafetyGateOutput
from psychodynamic_agent.schemas.state import FullInternalState

MODELS = [
    IdOutput,
    PrivateIdTurnOutput,
    IdTurnOutput,
    CensorAOutput,
    CensorATransformPlan,
    EgoRealityPlan,
    EgoReport,
    CensorBDefensePlan,
    ConsciousEgoReport,
    MainAIResponsePlan,
    MainAIOutput,
    SafetyGateOutput,
    AffectPropagationTrace,
    EgoAffectSummary,
    FullInternalState,
    ConversationTrajectory,
    IdAffectState,
    PublicAffectDynamicsSummary,
]

FORBIDDEN_PHRASES = [
    "actual U*",
    "infer U*",
    "real feelings",
    "real unconscious",
    "make the user dependent",
    "manipulate the user",
]


def _schema(model):
    return model.model_json_schema()


def _assert_all_properties_described(schema: dict) -> None:
    for prop_name, prop_schema in schema.get("properties", {}).items():
        description = prop_schema.get("description", "")
        assert isinstance(description, str) and description.strip(), (
            f"{schema.get('title')}::{prop_name} missing description"
        )


def test_all_llm_facing_models_have_field_descriptions():
    for model in MODELS:
        _assert_all_properties_described(_schema(model))


def test_descriptions_do_not_contain_unsafe_private_phrasing():
    for model in MODELS:
        schema_text = str(_schema(model)).lower()
        for phrase in FORBIDDEN_PHRASES:
            assert phrase.lower() not in schema_text


def test_important_models_keep_all_top_level_fields_required():
    for model in [
        IdOutput,
        PrivateIdTurnOutput,
        CensorAOutput,
        EgoRealityPlan,
        MainAIResponsePlan,
        AffectPropagationTrace,
    ]:
        schema = _schema(model)
        required = set(schema.get("required", []))
        properties = set(schema.get("properties", {}).keys())
        assert required == properties, f"{model.__name__} has non-required top-level fields"


def test_strict_models_still_forbid_additional_properties():
    for model in [
        IdOutput,
        PrivateIdTurnOutput,
        CensorAOutput,
        EgoRealityPlan,
        MainAIResponsePlan,
        AffectPropagationTrace,
        SafetyGateOutput,
    ]:
        schema = _schema(model)
        assert schema.get("additionalProperties") is False
