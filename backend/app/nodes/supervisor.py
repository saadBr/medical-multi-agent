from backend.app.state import MedicalState

def supervisor(state: MedicalState) -> dict:
    """
    Decide which agent should run next.
    """
    if not state.get("diagnostic_summary"):
        next_node = "diagnostic_agent"
    elif not state.get("interim_care"):
        next_node = "interim_care_agent"
    elif not state.get("physician_treatment"):
        next_node = "physician_review"
    elif not state.get("final_report"):
        next_node = "report_agent"
    else:
        next_node = "FINISH"

    return {"next": next_node}