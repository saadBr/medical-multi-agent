from backend.app.nodes.supervisor import supervisor


def test_supervisor_routes_to_diagnostic_agent():
    assert supervisor({})["next"] == "diagnostic_agent"


def test_supervisor_routes_to_interim_care_agent():
    state = {
        "diagnostic_summary": {"severity": "moderate"},
    }

    assert supervisor(state)["next"] == "interim_care_agent"


def test_supervisor_routes_to_physician_review():
    state = {
        "diagnostic_summary": {"severity": "moderate"},
        "interim_care": {"urgency": "routine"},
    }

    assert supervisor(state)["next"] == "physician_review"


def test_supervisor_routes_to_report_agent():
    state = {
        "diagnostic_summary": {"severity": "moderate"},
        "interim_care": {"urgency": "routine"},
        "physician_treatment": "Rest and monitor symptoms.",
    }

    assert supervisor(state)["next"] == "report_agent"


def test_supervisor_finishes_completed_workflow():
    state = {
        "diagnostic_summary": {"severity": "moderate"},
        "interim_care": {"urgency": "routine"},
        "physician_treatment": "Rest and monitor symptoms.",
        "final_report": {"title": "Final Medical Orientation Report"},
    }

    assert supervisor(state)["next"] == "FINISH"