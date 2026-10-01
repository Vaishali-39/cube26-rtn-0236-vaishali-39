import json
import sys
from pathlib import Path

import streamlit as st


# ============================================================
# Project setup
# ============================================================

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from returns_manager.main import analyze_return
from returns_manager.models import ReturnCase


# ============================================================
# Page configuration
# ============================================================

st.set_page_config(
    page_title="Returns Manager",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# Helper functions
# ============================================================

def verdict_icon(verdict):
    if verdict == "PASS":
        return "🟢"
    if verdict == "FAIL":
        return "🔴"
    return "🟡"


def display_evidence_reference(reference):
    """
    UI should not expose the local Windows path.
    Show only the evidence filename.
    """
    if not reference:
        return "Evidence"

    try:
        return Path(str(reference)).name
    except Exception:
        return str(reference)


def display_disposition(value):
    return str(value).replace("_", " ").title()


# ============================================================
# Header
# ============================================================

st.title("📦 Returns Manager")

st.write(
    "Evidence-driven return inspection for identity, completeness, "
    "condition and disposition decisions."
)

st.caption(
    "PASS = evidence supports the condition. "
    "FAIL = evidence supports that the condition is not met. "
    "UNCERTAIN = evidence is insufficient for a reliable judgment."
)

st.divider()


# ============================================================
# 1. RETURN EVIDENCE
# ============================================================

st.header("1. Return Evidence")

image_dir = ROOT / "fixtures" / "images" / "returns"

if not image_dir.exists():
    st.error(
        "Return image directory was not found: "
        "fixtures/images/returns"
    )
    st.stop()

available_images = sorted(
    [
        path
        for path in image_dir.iterdir()
        if path.is_file()
    ]
)

if not available_images:
    st.error(
        "No return evidence images were found in "
        "fixtures/images/returns."
    )
    st.stop()

image_names = [
    path.name for path in available_images
]

selected_image = st.selectbox(
    "Select return evidence",
    image_names,
)

selected_path = image_dir / selected_image


left, right = st.columns([1.2, 1])


with left:
    st.subheader("Evidence Image")

    st.image(
        str(selected_path),
        caption=selected_image,
        use_container_width=True,
    )


with right:
    st.subheader("Return Details")

    record_id = st.text_input(
        "Record ID",
        value="RTN-DEMO-001",
    )

    unit_id = st.text_input(
        "Unit ID",
        value="UNIT-DEMO-001",
    )

    organization = st.text_input(
        "Organization ID",
        value="org_demo_alpha",
    )

    ordered_sku = st.text_input(
        "Ordered SKU",
        value="SKU-DEMO-001",
    )

    ordered_asin = st.text_input(
        "Ordered ASIN",
        value="ASIN-DEMO-001",
    )

    st.info(
        "The selected fixture is passed through the existing "
        "Returns Manager analysis pipeline."
    )

    analyze_button = st.button(
        "🔍 Analyze Return",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button:

    if not record_id.strip():
        st.error("Record ID is required.")
        st.stop()

    if not unit_id.strip():
        st.error("Unit ID is required.")
        st.stop()

    if not organization.strip():
        st.error("Organization ID is required.")
        st.stop()

    case = ReturnCase(
        record_id=record_id.strip(),
        unit_id=unit_id.strip(),
        org_id=organization.strip(),
        photo_refs=[str(selected_path)],
        order_id="ORDER-DEMO-001",
        ordered_sku=ordered_sku.strip(),
        ordered_asin=ordered_asin.strip(),
        parts_list=[
            "carrying_case",
            "usb_cable",
            "manual",
        ],
        parts_missing=[],
    )

    try:
        with st.spinner("Analyzing return evidence..."):
            result = analyze_return(case)

        st.session_state["analysis_result"] = result

    except Exception as exc:
        st.error(
            "The Returns Manager could not complete the analysis."
        )
        st.exception(exc)
        st.stop()


# ============================================================
# WAIT FOR ANALYSIS
# ============================================================

if "analysis_result" not in st.session_state:

    st.divider()

    st.info(
        "Select a return image and click "
        "'Analyze Return' to generate the decision "
        "and evidence record."
    )

    st.stop()


# ============================================================
# RESULT
# ============================================================

result = st.session_state["analysis_result"]

record = result["record"]
checks = result["checks"]
disposition = result["recommended_disposition"]


# ============================================================
# 2. DECISION SUMMARY
# ============================================================

st.divider()

st.header("2. Decision Summary")

summary_columns = st.columns(4)

for column, check in zip(summary_columns, checks):

    with column:

        icon = verdict_icon(check.verdict)

        if check.verdict == "PASS":
            st.success(
                f"{icon} {check.check_key.upper()}"
            )

        elif check.verdict == "FAIL":
            st.error(
                f"{icon} {check.check_key.upper()}"
            )

        else:
            st.warning(
                f"{icon} {check.check_key.upper()}"
            )

        st.subheader(check.verdict)

        if check.confidence is not None:
            st.metric(
                "Confidence",
                f"{check.confidence:.2f}",
            )
        else:
            st.metric(
                "Confidence",
                "N/A",
            )


# ============================================================
# REVIEW HANDLING
# ============================================================

needs_review = (
    record.outcome == "UNCERTAIN"
    or disposition == "pending_review"
    or any(
        check.verdict == "UNCERTAIN"
        for check in checks
    )
)

if needs_review:
    st.warning(
        "🔎 Human review required. "
        "The available evidence does not support a fully "
        "reliable automatic decision."
    )


# ============================================================
# 3. OVERALL DECISION
# ============================================================

st.divider()

st.header("3. Overall Decision")

decision_col1, decision_col2 = st.columns(2)


with decision_col1:

    st.subheader("Recommended Disposition")

    if disposition == "pending_review":
        st.warning("🔎 Pending Review")
    else:
        st.success(
            display_disposition(disposition)
        )


with decision_col2:

    st.subheader("Overall Outcome")

    if record.outcome == "PASS":
        st.success("PASS")

    elif record.outcome == "FAIL":
        st.error("FAIL")

    else:
        st.warning("UNCERTAIN")


# ============================================================
# 4. RETURN INFORMATION
# ============================================================

st.divider()

st.header("4. Return Information")

info_col1, info_col2, info_col3, info_col4 = st.columns(4)


with info_col1:
    st.metric(
        "Record ID",
        record.record_id,
    )


with info_col2:

    unit_value = "N/A"

    if isinstance(record.subject, dict):
        unit_value = record.subject.get(
            "unit_id",
            "N/A",
        )

    st.metric(
        "Unit ID",
        unit_value,
    )


with info_col3:
    st.metric(
        "Organization",
        record.organization_id,
    )


with info_col4:

    status_value = display_disposition(
        record.status
    )

    st.metric(
        "Status",
        status_value,
    )


# ============================================================
# 5. EVIDENCE & TRACEABILITY
# ============================================================

st.divider()

st.header("5. Evidence & Traceability")

st.write(
    "Each check shows the decision, confidence, supporting "
    "detail and evidence used by the Returns Manager."
)


for check in checks:

    icon = verdict_icon(check.verdict)

    with st.expander(
        f"{icon} {check.check_key.upper()} — {check.verdict}",
        expanded=False,
    ):

        st.write("**Decision detail**")

        st.write(check.detail)


        detail_col1, detail_col2 = st.columns(2)


        with detail_col1:

            st.write("**Verdict**")

            st.write(check.verdict)


        with detail_col2:

            st.write("**Confidence**")

            if check.confidence is not None:
                st.write(
                    f"{check.confidence:.2f}"
                )
            else:
                st.write("N/A")


        if check.model_version:
            st.caption(
                f"Model version: {check.model_version}"
            )


        if check.latency_ms is not None:
            st.caption(
                f"Latency: {check.latency_ms:.2f} ms"
            )


        if check.evidence_refs:

            st.write("**Evidence**")

            for reference in check.evidence_refs:

                filename = display_evidence_reference(
                    reference
                )

                st.markdown(
                    f"📎 `{filename}`"
                )

        else:

            st.caption(
                "No separate evidence reference was attached "
                "to this check."
            )


# ============================================================
# 6. STRUCTURED EVIDENCE RECORD
# ============================================================

st.divider()

st.header("6. Structured Evidence Record")

st.write(
    "The evidence record contains the structured fields needed "
    "for downstream interoperability."
)


# ------------------------------------------------------------
# Official evidence record
# ------------------------------------------------------------

record_data = {
    "record_id": record.record_id,
    "schema_version": record.schema_version,
    "organization_id": record.organization_id,
    "client_id": record.client_id,
    "agent": record.agent,
    "subject": record.subject,
    "captured_at": record.captured_at,
    "operator_label": record.operator_label,
    "images": record.images,
    "checks": [
        {
            "check_key": check.check_key,
            "verdict": check.verdict,
            "confidence": check.confidence,
            "detail": check.detail,
            "model_version": check.model_version,
            "latency_ms": check.latency_ms,
            "evidence_refs": check.evidence_refs,
        }
        for check in record.checks
    ],
    "outcome": record.outcome,
    "overrides": [
        {
            "original_verdict": override.original_verdict,
            "revised_verdict": override.revised_verdict,
            "reason": override.reason,
            "operator_id": override.operator_id,
        }
        for override in record.overrides
    ],
    "status": record.status,
    "content_hash": record.content_hash,
}


# ------------------------------------------------------------
# UI-safe preview
# ------------------------------------------------------------

ui_record_data = dict(record_data)

ui_record_data["images"] = [
    display_evidence_reference(image)
    for image in record.images
]

ui_record_data["checks"] = []

for check in record.checks:

    ui_check = {
        "check_key": check.check_key,
        "verdict": check.verdict,
        "confidence": check.confidence,
        "detail": check.detail,
        "model_version": check.model_version,
        "latency_ms": check.latency_ms,
        "evidence_refs": [
            display_evidence_reference(reference)
            for reference in check.evidence_refs
        ],
    }

    ui_record_data["checks"].append(
        ui_check
    )


with st.expander(
    "View structured evidence record",
    expanded=False,
):

    st.json(ui_record_data)


# ============================================================
# DOWNLOAD EXACT STRUCTURED RECORD
# ============================================================

json_data = json.dumps(
    record_data,
    indent=2,
    default=str,
)


st.download_button(
    label="⬇️ Download Evidence JSON",
    data=json_data,
    file_name=f"{record.record_id}.json",
    mime="application/json",
    use_container_width=True,
)


# ============================================================
# 7. DEMO NOTES
# ============================================================

st.divider()

st.header("7. Demo Notes")

st.write(
    "The Returns Manager processes return evidence through "
    "identity, completeness, condition and disposition checks. "
    "The resulting evidence record is structured for downstream "
    "use by the Recovery Manager."
)

st.caption(
    "UNCERTAIN is preserved when the available evidence is "
    "insufficient for a reliable judgment."
)