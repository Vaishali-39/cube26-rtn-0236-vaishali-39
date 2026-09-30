from src.returns_manager.models import (
    CheckResult,
    Override,
    ReturnCase,
)
from src.returns_manager.evidence import (
    determine_overall_outcome,
    add_evidence_reference,
    build_evidence_record,
)


def make_check(
    check_key,
    verdict,
    detail="",
    confidence=1.0,
):
    return CheckResult(
        check_key=check_key,
        verdict=verdict,
        confidence=confidence,
        detail=detail,
    )


def make_case():
    return ReturnCase(
        record_id="RTN-TEST-001",
        unit_id="UNIT-TEST-001",
        org_id="org_demo_alpha",
        photo_refs=[
            "image_01.jpg",
            "image_02.jpg",
        ],
        operator_id="OP-001",
        captured_at="2026-09-30T10:00:00+00:00",
        order_id="ORDER-001",
        ordered_sku="SKU-001",
        ordered_asin="ASIN-001",
        identity_match="yes",
        parts_list=["case", "cable", "manual"],
        parts_missing=[],
        observed_state="opened_unused",
        amazon_condition="New",
        operator_disposition="restock",
    )


def test_no_checks_produces_uncertain():
    result = determine_overall_outcome([])

    assert result == "UNCERTAIN"


def test_all_pass_produces_pass():
    checks = [
        make_check("identity", "PASS"),
        make_check("completeness", "PASS"),
        make_check("condition", "PASS"),
    ]

    result = determine_overall_outcome(checks)

    assert result == "PASS"


def test_fail_produces_fail():
    checks = [
        make_check("identity", "PASS"),
        make_check("completeness", "FAIL"),
        make_check("condition", "PASS"),
    ]

    result = determine_overall_outcome(checks)

    assert result == "FAIL"


def test_uncertain_takes_precedence_over_fail():
    checks = [
        make_check("identity", "FAIL"),
        make_check("completeness", "UNCERTAIN"),
        make_check("condition", "PASS"),
    ]

    result = determine_overall_outcome(checks)

    assert result == "UNCERTAIN"


def test_add_evidence_reference():
    check = make_check(
        "identity",
        "PASS",
    )

    result = add_evidence_reference(
        check,
        "image_01",
    )

    assert result.evidence_refs == ["image_01"]


def test_duplicate_evidence_reference_is_not_added():
    check = make_check(
        "identity",
        "PASS",
    )

    add_evidence_reference(
        check,
        "image_01",
    )

    add_evidence_reference(
        check,
        "image_01",
    )

    assert check.evidence_refs == ["image_01"]


def test_build_evidence_record_contains_required_fields():
    case = make_case()

    checks = [
        make_check(
            "identity",
            "PASS",
            "Identity matches.",
        ),
        make_check(
            "completeness",
            "PASS",
            "All parts are present.",
        ),
        make_check(
            "condition",
            "PASS",
            "Condition classified as New.",
        ),
    ]

    record = build_evidence_record(
        case,
        checks,
        client_id="client_demo",
    )

    assert record.record_id == "RTN-TEST-001"
    assert record.schema_version == "1.0"
    assert record.organization_id == "org_demo_alpha"
    assert record.client_id == "client_demo"
    assert record.agent == "returns-manager"
    assert record.subject["unit_id"] == "UNIT-TEST-001"
    assert record.images == [
        "image_01.jpg",
        "image_02.jpg",
    ]
    assert len(record.checks) == 3
    assert record.outcome == "PASS"
    assert record.status == "completed"


def test_evidence_record_contains_content_hash():
    case = make_case()

    checks = [
        make_check("identity", "PASS"),
        make_check("completeness", "PASS"),
        make_check("condition", "PASS"),
    ]

    record = build_evidence_record(
        case,
        checks,
    )

    assert record.content_hash is not None
    assert len(record.content_hash) == 64


def test_evidence_record_preserves_override():
    case = make_case()

    checks = [
        make_check("identity", "PASS"),
        make_check("completeness", "PASS"),
        make_check("condition", "PASS"),
    ]

    override = Override(
        original_verdict="PASS",
        revised_verdict="FAIL",
        reason="Operator found visible damage.",
        operator_id="OP-001",
    )

    record = build_evidence_record(
        case,
        checks,
        overrides=[override],
    )

    assert len(record.overrides) == 1
    assert record.overrides[0].reason == (
        "Operator found visible damage."
    )