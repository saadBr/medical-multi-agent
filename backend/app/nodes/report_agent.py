from backend.app.state import MedicalState

DISCLAIMER = "This system does not replace a medical consultation."

def report_agent(state: MedicalState)-> dict:
    """
    Generate a temporary final report from the graph state.
    """

    final_report = (
        "FINAL MEDICAL ORIENTATION REPORT\n\n"
        f"Initial case: {state.get('initial_case', '')}\n\n"
        f"Preliminary summary: {state.get('diagnostic_summary', '')}\n\n"
        f"Physician recommendation: "
        f"{state.get('physician_treatment', '')}\n\n"
        f"Physician notes: {state.get('physician_notes', '')}\n\n"
        f"{DISCLAIMER}"
    )

    return {"final_report":final_report}
