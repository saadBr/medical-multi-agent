from backend.app.state import MedicalState

def physician_review(state: MedicalState)-> dict:
    """
    Temporarily simulate the physician's review.
    """

    return {
        "physician_treatment": "Temporary physician recommendation.",
        "physician_notes": "This will later be replaced by human input",
    }