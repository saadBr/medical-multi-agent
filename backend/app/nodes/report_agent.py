from backend.app.schemas import FinalReport
from backend.app.state import MedicalState


DISCLAIMER = "This system does not replace a medical consultation."


def report_agent(state: MedicalState) -> dict:
    """Build the final structured medical-orientation report."""

    report = FinalReport(
        initial_case=state.get("initial_case", ""),
        preliminary_summary=state["diagnostic_summary"],
        interim_care=state["interim_care"],
        physician_recommendation=state.get(
            "physician_treatment",
            "",
        ),
        physician_notes=state.get("physician_notes", ""),
        disclaimer=DISCLAIMER,
    )

    return {
        "final_report": report.model_dump(),
    }