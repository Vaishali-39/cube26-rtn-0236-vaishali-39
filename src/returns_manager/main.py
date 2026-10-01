from .vision_pipeline import (
    analyze_case_images,
    apply_vision_observation,
    aggregate_observations,
)
from .models import ReturnCase, CheckResult
from .identity import assess_identity
from .completeness import assess_completeness
from .condition import assess_condition
from .disposition import disposition_check, recommend_disposition
from .evidence import build_evidence_record


def analyze_return(case: ReturnCase):
    """
    Run the complete Returns Manager workflow for one returned unit.

    Workflow:

        Photos
            ↓
        Vision observations
            ↓
        Identity
            ↓
        Completeness
            ↓
        Condition
            ↓
        Disposition
            ↓
        Evidence Record
    """

    # ---------------------------------------------------------
    # 0. Vision observations
    # ---------------------------------------------------------

    observations = analyze_case_images(case)

    aggregated_observation = aggregate_observations(
        observations
    )

    if aggregated_observation is not None:
        apply_vision_observation(
            case,
            aggregated_observation,
        )

    # ---------------------------------------------------------
    # 1. Identity
    # ---------------------------------------------------------

    identity_result = assess_identity(case)

    # ---------------------------------------------------------
    # 2. Completeness
    # ---------------------------------------------------------

    completeness_result = assess_completeness(case)

    # ---------------------------------------------------------
    # 3. Condition
    # ---------------------------------------------------------

    condition_result = assess_condition(case)

    # ---------------------------------------------------------
    # 4. Recommended disposition
    # ---------------------------------------------------------

    disposition_result = disposition_check(
        identity=identity_result,
        completeness=completeness_result,
        condition=condition_result,
    )

    recommended_disposition = recommend_disposition(
        identity=identity_result,
        completeness=completeness_result,
        condition=condition_result,
    )

    # ---------------------------------------------------------
    # 5. Collect all checks
    # ---------------------------------------------------------

    checks = [
        identity_result,
        completeness_result,
        condition_result,
        disposition_result,
    ]

    # ---------------------------------------------------------
    # 6. Build final evidence record
    # ---------------------------------------------------------

    evidence_record = build_evidence_record(
        case=case,
        checks=checks,
    )

    return {
        "record": evidence_record,
        "recommended_disposition": recommended_disposition,
        "checks": checks,
    }


def print_result(result):
    """
    Print a human-readable summary for local testing/demo.
    """

    record = result["record"]
    checks = result["checks"]

    print("=" * 60)
    print("RETURNS MANAGER")
    print("=" * 60)

    print(f"Record ID: {record.record_id}")
    print(f"Unit ID: {record.subject.get('unit_id')}")
    print(f"Organization: {record.organization_id}")
    print()

    for check in checks:
        print(f"{check.check_key.upper()}:")
        print(f"  Verdict: {check.verdict}")
        print(f"  Confidence: {check.confidence}")
        print(f"  Evidence: {check.detail}")
        print()

    print(
        f"Recommended disposition: "
        f"{result['recommended_disposition']}"
    )

    print(f"Overall outcome: {record.outcome}")

    print("=" * 60)


if __name__ == "__main__":
    # Simple local test case.
    #
    # This is only a development fixture.
    # It is NOT evaluation data.

    test_case = ReturnCase(
        record_id="RTN-TEST-001",
        unit_id="UNIT-TEST-001",
        org_id="org_demo_alpha",
        photo_refs=[
            "fixtures/images/test_return_01.jpg"
        ],
        order_id="ORDER-TEST-001",
        ordered_sku="SKU-TEST-001",
        ordered_asin="ASIN-TEST-001",
        identity_match="yes",
        parts_list=[
            "carrying_case",
            "usb_cable",
            "manual",
        ],
        parts_missing=[],
        observed_state="opened_unused",
    )

    result = analyze_return(test_case)

    print_result(result)