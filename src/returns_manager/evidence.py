from datetime import datetime, timezone
import hashlib
import json
from typing import Optional

from .models import (
    CheckResult,
    EvidenceRecord,
    Override,
    ReturnCase,
)


SCHEMA_VERSION = "1.0"

AGENT_NAME = "returns-manager"


def determine_overall_outcome(
    checks: list[CheckResult],
) -> str:
    """
    Determine the overall outcome of the evidence record.

    UNCERTAIN takes precedence over FAIL because ambiguous
    evidence must not be represented as a definite failure.
    """

    if not checks:
        return "UNCERTAIN"

    if any(check.verdict == "UNCERTAIN" for check in checks):
        return "UNCERTAIN"

    if any(check.verdict == "FAIL" for check in checks):
        return "FAIL"

    return "PASS"


def add_evidence_reference(
    check: CheckResult,
    evidence_ref: str,
) -> CheckResult:
    """
    Add a reference to supporting evidence.

    Example references:

        image_01
        image_02
        operator_note_01
    """

    if evidence_ref and evidence_ref not in check.evidence_refs:
        check.evidence_refs.append(evidence_ref)

    return check


def attach_image_evidence(
    checks: list[CheckResult],
    image_refs: list[str],
) -> list[CheckResult]:
    """
    Attach supplied image references to every check.

    This makes each business check traceable back to the
    images available during return analysis.
    """

    for check in checks:
        for image_ref in image_refs:
            add_evidence_reference(
                check,
                image_ref,
            )

    return checks


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO-8601 format.
    """

    return datetime.now(timezone.utc).isoformat()


def _serialize_check(check: CheckResult) -> dict:
    """
    Convert a CheckResult into a stable dictionary.
    """

    return {
        "check_key": check.check_key,
        "verdict": check.verdict,
        "confidence": check.confidence,
        "detail": check.detail,
        "model_version": check.model_version,
        "latency_ms": check.latency_ms,
        "evidence_refs": sorted(check.evidence_refs),
    }


def _serialize_override(override: Override) -> dict:
    """
    Convert an Override into a stable dictionary.
    """

    return {
        "original_verdict": override.original_verdict,
        "revised_verdict": override.revised_verdict,
        "reason": override.reason,
        "operator_id": override.operator_id,
    }


def _calculate_content_hash(
    *,
    record_id: str,
    schema_version: str,
    organization_id: str,
    client_id: Optional[str],
    agent: str,
    subject: dict,
    captured_at: Optional[str],
    operator_label: Optional[str],
    images: list[str],
    checks: list[CheckResult],
    outcome: str,
    overrides: list[Override],
    status: str,
) -> str:
    """
    Create a deterministic SHA-256 hash of the evidence content.

    The hash helps detect accidental or unauthorized changes
    to the evidence record.
    """

    canonical_data = {
        "record_id": record_id,
        "schema_version": schema_version,
        "organization_id": organization_id,
        "client_id": client_id,
        "agent": agent,
        "subject": subject,
        "captured_at": captured_at,
        "operator_label": operator_label,
        "images": sorted(images),
        "checks": [
            _serialize_check(check)
            for check in checks
        ],
        "outcome": outcome,
        "overrides": [
            _serialize_override(override)
            for override in overrides
        ],
        "status": status,
    }

    canonical_json = json.dumps(
        canonical_data,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )

    return hashlib.sha256(
        canonical_json.encode("utf-8")
    ).hexdigest()

def attach_image_evidence(
    checks: list[CheckResult],
    image_refs: list[str],
) -> list[CheckResult]:
    """
    Attach all available image references to each check.

    Existing references are preserved and duplicates are avoided.
    """

    for check in checks:
        for image_ref in image_refs:
            add_evidence_reference(check, image_ref)

    return checks


def build_evidence_record(
    case: ReturnCase,
    checks: list[CheckResult],
    *,
    client_id: Optional[str] = None,
    operator_label: Optional[str] = None,
    agent: str = AGENT_NAME,
    status: str = "completed",
    overrides: Optional[list[Override]] = None,
) -> EvidenceRecord:
    """
    Build the complete structured evidence record.
    """

    final_overrides = overrides or []

    # Attach the case images to each business check so that
    # every decision can be traced back to its supporting images.
    attach_image_evidence(
        checks,
        case.photo_refs,
    )

    outcome = determine_overall_outcome(checks)

    subject = {
        "unit_id": case.unit_id,
        "order_id": case.order_id,
        "ordered_sku": case.ordered_sku,
        "ordered_asin": case.ordered_asin,
        "identity_match": case.identity_match,
        "parts_list": case.parts_list,
        "parts_missing": case.parts_missing,
        "observed_state": case.observed_state,
        "amazon_condition": case.amazon_condition,
        "operator_disposition": case.operator_disposition,
    }

    content_hash = _calculate_content_hash(
        record_id=case.record_id,
        schema_version=SCHEMA_VERSION,
        organization_id=case.org_id,
        client_id=client_id,
        agent=agent,
        subject=subject,
        captured_at=case.captured_at,
        operator_label=operator_label or case.operator_id,
        images=case.photo_refs,
        checks=checks,
        outcome=outcome,
        overrides=final_overrides,
        status=status,
    )

    return EvidenceRecord(
        record_id=case.record_id,
        schema_version=SCHEMA_VERSION,
        organization_id=case.org_id,
        client_id=client_id,
        agent=agent,
        subject=subject,
        captured_at=case.captured_at,
        operator_label=operator_label or case.operator_id,
        images=case.photo_refs,
        checks=checks,
        outcome=outcome,
        overrides=final_overrides,
        status=status,
        content_hash=content_hash,
    )
