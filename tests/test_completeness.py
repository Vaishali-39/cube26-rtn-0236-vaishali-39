from src.returns_manager.models import ReturnCase
from src.returns_manager.completeness import assess_completeness


def make_case(parts_list=None, parts_missing=None):
    return ReturnCase(
        record_id="RTN-TEST-002",
        unit_id="UNIT-TEST-002",
        org_id="org_demo_alpha",
        parts_list=parts_list or [],
        parts_missing=parts_missing or [],
    )


def test_all_parts_present():
    case = make_case(
        parts_list=["charger", "manual", "cable"],
        parts_missing=[],
    )

    result = assess_completeness(case)

    assert result.check_key == "completeness"
    assert result.verdict == "PASS"
    assert result.confidence == 1.0


def test_one_part_missing():
    case = make_case(
        parts_list=["charger", "manual", "cable"],
        parts_missing=["cable"],
    )

    result = assess_completeness(case)

    assert result.check_key == "completeness"
    assert result.verdict == "FAIL"
    assert "cable" in result.detail


def test_multiple_parts_missing():
    case = make_case(
        parts_list=["charger", "manual", "cable", "case"],
        parts_missing=["cable", "case"],
    )

    result = assess_completeness(case)

    assert result.verdict == "FAIL"
    assert "cable" in result.detail
    assert "case" in result.detail


def test_no_expected_parts_is_uncertain():
    case = make_case(
        parts_list=[],
        parts_missing=[],
    )

    result = assess_completeness(case)

    assert result.verdict == "UNCERTAIN"

def test_missing_parts_without_expected_list():
    case = make_case(
        parts_list=[],
        parts_missing=["cable"],
    )

    result = assess_completeness(case)

    assert result.verdict == "FAIL"