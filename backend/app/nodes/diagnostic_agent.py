from backend.app.state import MedicalState

def diagnostic_agent(state: MedicalState)-> dict:
    """
    Create a temporary preliminary clinical summary.
    """

    initial_case = state.get("initial_case", "No initial case provided")

    summary = (
        f"Preliminary clinical summary based on the initial case: "
        f"{initial_case}"
    )

    return {
        "diagnostic_summary": summary,
    }