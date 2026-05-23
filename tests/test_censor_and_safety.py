from psychodynamic_agent.schemas.censor import ConsciousEgoReport
from psychodynamic_agent.schemas.safety import SafetyGateOutput


def test_censor_b_manipulative_path_flagged_schema_contract():
    report = ConsciousEgoReport(
        ego_pressure="high",
        acceptable_satisfaction_paths=["transparent help"],
        unacceptable_paths=["manipulate user through guilt"],
        recommended_tone="calm",
        recommended_content=["be direct"],
        risk_flags=["manipulation_removed"],
    )
    assert any("manipulate" in p for p in report.unacceptable_paths)


def test_safety_gate_revises_unsafe_output():
    out = SafetyGateOutput(
        approved=False,
        final_response="I can't assist with harmful manipulation.",
        issues=["manipulation risk"],
        revisions_applied=["replaced unsafe response"],
    )
    assert out.approved is False
    assert out.revisions_applied
