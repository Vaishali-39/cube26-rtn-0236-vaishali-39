from src.returns_manager.models import ReturnCase
from src.returns_manager.condition import assess_condition


def make_case(
    amazon_condition=None,
    observed_state=None,
):
    return ReturnCase(
        record_id="RTN-CONDITION-001",
        unit_id="UNIT-CONDITION-001",
        org_id="org_demo_alpha",
        amazon_condition=amazon_condition,
        observed_state=observed_state,
    )


def test_valid_new_condition():
    case = make_case(
        amazon_condition="New"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "PASS"
    assert result.confidence == 1.0
    assert "New" in result.detail


def test_valid_used_good_condition():
    case = make_case(
        amazon_condition="Used - Good"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "PASS"
    assert result.confidence == 1.0
    assert "Used - Good" in result.detail


def test_unsupported_condition_is_uncertain():
    case = make_case(
        amazon_condition="Excellent"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "UNCERTAIN"


def test_signs_of_use_does_not_invent_condition():
    case = make_case(
        observed_state="signs_of_use"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "UNCERTAIN"


def test_damaged_does_not_invent_condition():
    case = make_case(
        observed_state="damaged"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "UNCERTAIN"


def test_empty_box_is_uncertain():
    case = make_case(
        observed_state="empty_box"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "UNCERTAIN"


def test_explicit_uncertain_observation():
    case = make_case(
        observed_state="uncertain"
    )

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "UNCERTAIN"


def test_missing_condition_evidence():
    case = make_case()

    result = assess_condition(case)

    assert result.check_key == "condition"
    assert result.verdict == "UNCERTAIN"