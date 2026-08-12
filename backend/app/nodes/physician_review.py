from langgraph.types import interrupt

from backend.app.state import MedicalState


def physician_review(state: MedicalState) -> dict:
    """Pause the workflow and request a physician's review."""

    review = interrupt(
        {
            "type": "physician_review",
            "diagnostic_summary": state.get("diagnostic_summary", ""),
            "interim_care": state.get("interim_care", ""),
            "instructions": (
                "Review the preliminary summary and provide a treatment "
                "or recommended course of action."
            ),
        }
    )

    return {
        "physician_treatment": review["treatment"],
        "physician_notes": review.get("notes", ""),
    }