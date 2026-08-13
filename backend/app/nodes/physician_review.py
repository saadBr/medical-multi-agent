from langgraph.types import interrupt

from backend.app.state import MedicalState
import json

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

    if isinstance(review, str):
        review = json.loads(review)

    if not isinstance(review, dict):
        raise ValueError("Physician review must be a JSON object.")

    return {
        "physician_treatment": review["treatment"],
        "physician_notes": review.get("notes", ""),
    }