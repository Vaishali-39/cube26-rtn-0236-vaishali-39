from src.returns_manager.models import CheckResult
from src.returns_manager.disposition import (
    recommend_disposition,
    disposition_check,
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


def test_complete_identified_good_item_is_restocked():
    identity = make_check(
        "identity",
        "PASS",
        "Returned item identity matches the ordered item.",
    )

    completeness = make_check(
        "completeness",
        "PASS",
        "All expected parts are present.",
    )

    condition = make_check(
        "condition",
        "PASS",
        "Condition classified as 'New'.",
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "restock"


def test_missing_accessory_requires_refurbishment():
    identity = make_check(
        "identity",
        "PASS",
        "Returned item identity matches the ordered item.",
    )

    completeness = make_check(
        "completeness",
        "FAIL",
        "Expected parts are missing: cable.",
    )

    condition = make_check(
        "condition",
        "PASS",
        "Condition classified as 'Used - Good'.",
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "refurbish"


def test_identity_uncertain_requires_review():
    identity = make_check(
        "identity",
        "UNCERTAIN",
        "Identity could not be determined.",
        confidence=0.4,
    )

    completeness = make_check(
        "completeness",
        "PASS",
        "All expected parts are present.",
    )

    condition = make_check(
        "condition",
        "PASS",
        "Condition classified as 'New'.",
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "pending_review"


def test_wrong_product_requires_review():
    identity = make_check(
        "identity",
        "FAIL",
        "Returned item does not match the ordered item.",
    )

    completeness = make_check(
        "completeness",
        "PASS",
        "All expected parts are present.",
    )

    condition = make_check(
        "condition",
        "PASS",
        "Condition classified as 'New'.",
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "pending_review"


def test_completeness_uncertain_requires_review():
    identity = make_check(
        "identity",
        "PASS",
        "Returned item identity matches the ordered item.",
    )

    completeness = make_check(
        "completeness",
        "UNCERTAIN",
        "The expected parts list is unavailable.",
        confidence=0.3,
    )

    condition = make_check(
        "condition",
        "PASS",
        "Condition classified as 'New'.",
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "pending_review"


def test_condition_uncertain_requires_review():
    identity = make_check(
        "identity",
        "PASS",
        "Returned item identity matches the ordered item.",
    )

    completeness = make_check(
        "completeness",
        "PASS",
        "All expected parts are present.",
    )

    condition = make_check(
        "condition",
        "UNCERTAIN",
        "Insufficient evidence to assign a published condition grade.",
        confidence=0.4,
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "pending_review"


def test_damaged_item_is_refurbished():
    identity = make_check(
        "identity",
        "PASS",
        "Returned item identity matches the ordered item.",
    )

    completeness = make_check(
        "completeness",
        "PASS",
        "All expected parts are present.",
    )

    condition = make_check(
        "condition",
        "PASS",
        "Product is damaged and requires repair.",
    )

    result = recommend_disposition(
        identity,
        completeness,
        condition,
    )

    assert result == "refurbish"


def test_disposition_check_for_restock():
    identity = make_check("identity", "PASS")
    completeness = make_check("completeness", "PASS")
    condition = make_check("condition", "PASS")

    result = disposition_check(
        identity,
        completeness,
        condition,
    )

    assert result.check_key == "disposition"
    assert result.verdict == "PASS"
    assert result.confidence == 1.0
    assert "restock" in result.detail


def test_disposition_check_for_pending_review():
    identity = make_check("identity", "UNCERTAIN")
    completeness = make_check("completeness", "PASS")
    condition = make_check("condition", "PASS")

    result = disposition_check(
        identity,
        completeness,
        condition,
    )

    assert result.check_key == "disposition"
    assert result.verdict == "UNCERTAIN"
    assert result.confidence == 0.0