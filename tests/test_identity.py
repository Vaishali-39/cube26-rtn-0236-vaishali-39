from src.returns_manager.models import ReturnCase
from src.returns_manager.identity import assess_identity


def make_case(identity_match=None):
    return ReturnCase(
        record_id="RTN-TEST-001",
        unit_id="UNIT-TEST-001",
        org_id="org_demo_alpha",
        identity_match=identity_match,
    )


def test_identity_match_passes():
    result = assess_identity(make_case("yes"))

    assert result.check_key == "identity"
    assert result.verdict == "PASS"
    assert result.confidence == 1.0


def test_identity_mismatch_fails():
    result = assess_identity(make_case("no"))

    assert result.check_key == "identity"
    assert result.verdict == "FAIL"
    assert result.confidence == 1.0


def test_identity_uncertain():
    result = assess_identity(make_case("uncertain"))

    assert result.check_key == "identity"
    assert result.verdict == "UNCERTAIN"


def test_identity_missing_is_uncertain():
    result = assess_identity(make_case())

    assert result.check_key == "identity"
    assert result.verdict == "UNCERTAIN"


def test_identity_unsupported_value_is_uncertain():
    result = assess_identity(make_case("unknown"))

    assert result.check_key == "identity"
    assert result.verdict == "UNCERTAIN"