from src.returns_manager.main import analyze_return
from src.returns_manager.models import ReturnCase


def make_case(
    identity_match="yes",
    parts_list=None,
    parts_missing=None,
    amazon_condition="New",
    observed_state="factory_sealed",
):
    return ReturnCase(
        record_id="RTN-MAIN-001",
        unit_id="UNIT-MAIN-001",
        org_id="org_demo_alpha",
        photo_refs=[
            "fixtures/images/test_return_01.jpg"
        ],
        order_id="ORDER-MAIN-001",
        ordered_sku="SKU-MAIN-001",
        ordered_asin="ASIN-MAIN-001",
        identity_match=identity_match,
        parts_list=parts_list or [
            "carrying_case",
            "usb_cable",
            "manual",
        ],
        parts_missing=parts_missing or [],
        observed_state=observed_state,
        amazon_condition=amazon_condition,
    )


def test_complete_return_flows_to_restock():
    case = make_case()

    result = analyze_return(case)

    assert result["recommended_disposition"] == "restock"
    assert result["checks"][0].verdict == "PASS"
    assert result["checks"][1].verdict == "PASS"
    assert result["checks"][2].verdict == "PASS"
    assert result["record"].record_id == "RTN-MAIN-001"
    assert result["record"].outcome == "PASS"


def test_missing_accessory_flows_to_refurbish():
    case = make_case(
        parts_missing=["usb_cable"],
    )

    result = analyze_return(case)

    assert result["recommended_disposition"] == "refurbish"
    assert result["checks"][1].verdict == "FAIL"


def test_wrong_product_flows_to_pending_review():
    case = make_case(
        identity_match="no",
    )

    result = analyze_return(case)

    assert result["recommended_disposition"] == "pending_review"
    assert result["checks"][0].verdict == "FAIL"


def test_uncertain_identity_flows_to_pending_review():
    case = make_case(
        identity_match="uncertain",
    )

    result = analyze_return(case)

    assert result["recommended_disposition"] == "pending_review"
    assert result["checks"][0].verdict == "UNCERTAIN"


def test_uncertain_condition_flows_to_pending_review():
    case = make_case(
        amazon_condition=None,
        observed_state="uncertain",
    )

    result = analyze_return(case)

    assert result["recommended_disposition"] == "pending_review"
    assert result["checks"][2].verdict == "UNCERTAIN"


def test_evidence_record_contains_all_checks():
    case = make_case()

    result = analyze_return(case)

    check_keys = [
        check.check_key
        for check in result["record"].checks
    ]

    assert "identity" in check_keys
    assert "completeness" in check_keys
    assert "condition" in check_keys
    assert "disposition" in check_keys


def test_evidence_record_has_content_hash():
    case = make_case()

    result = analyze_return(case)

    assert result["record"].content_hash is not None
    assert len(result["record"].content_hash) == 64