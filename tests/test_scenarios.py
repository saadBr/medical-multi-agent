from uuid import uuid4

import pytest
from langgraph.types import Command

import backend.app.nodes.diagnostic_agent as diagnostic_module
import backend.app.nodes.interim_care_agent as care_module
from backend.app.graph import graph
from backend.app.schemas import ClinicalSummary


class FakeStructuredLLM:
    def __init__(self, summary: dict):
        self.summary = summary

    def invoke(self, messages):
        return ClinicalSummary(**self.summary)


class FakeLLM:
    def __init__(self, summary: dict):
        self.summary = summary

    def with_structured_output(self, schema):
        return FakeStructuredLLM(self.summary)


SCENARIOS = [
    {
        "name": "simple_respiratory_case",
        "initial_case": "The patient reports cough and mild fever.",
        "answers": [
            "Two days ago",
            "5",
            "Sore throat",
            "No known conditions or allergies",
            "No warning signs",
        ],
        "summary": {
            "main_complaint": "Cough and mild fever",
            "symptoms": ["cough", "mild fever", "sore throat"],
            "duration": "Two days",
            "severity": "moderate",
            "relevant_history": [],
            "warning_signs": [],
            "preliminary_orientation": (
                "Respiratory symptoms requiring monitoring."
            ),
        },
        "expected_urgency": "routine",
    },
    {
        "name": "case_with_red_flags",
        "initial_case": "The patient reports fever and chest pain.",
        "answers": [
            "One day ago",
            "8",
            "Shortness of breath",
            "No known allergies",
            "Chest pain and difficulty breathing",
        ],
        "summary": {
            "main_complaint": "Fever and chest pain",
            "symptoms": ["fever", "chest pain", "shortness of breath"],
            "duration": "One day",
            "severity": "high",
            "relevant_history": [],
            "warning_signs": [
                "chest pain",
                "difficulty breathing",
            ],
            "preliminary_orientation": (
                "Warning signs require prompt professional evaluation."
            ),
        },
        "expected_urgency": "urgent",
    },
    {
        "name": "benign_case",
        "initial_case": "The patient reports a mild headache.",
        "answers": [
            "This morning",
            "2",
            "No other symptoms",
            "No known conditions or allergies",
            "No warning signs",
        ],
        "summary": {
            "main_complaint": "Mild headache",
            "symptoms": ["mild headache"],
            "duration": "Since this morning",
            "severity": "low",
            "relevant_history": [],
            "warning_signs": [],
            "preliminary_orientation": (
                "Mild symptoms suitable for routine monitoring."
            ),
        },
        "expected_urgency": "routine",
    },
]


@pytest.mark.asyncio
@pytest.mark.parametrize("scenario", SCENARIOS, ids=lambda item: item["name"])
async def test_complete_medical_workflow(monkeypatch, scenario):
    monkeypatch.setattr(
        diagnostic_module,
        "llm",
        FakeLLM(scenario["summary"]),
    )

    def fake_mcp_tool(severity, warning_signs):
        urgency = (
            "urgent"
            if warning_signs or severity == "high"
            else "routine"
        )
        return {
            "urgency": urgency,
            "recommendations": ["Academic interim guidance."],
        }

    monkeypatch.setattr(
        care_module,
        "run_mcp_tool",
        fake_mcp_tool,
    )

    config = {
        "configurable": {
            "thread_id": str(uuid4()),
        }
    }

    result = await graph.ainvoke(
        {
            "initial_case": scenario["initial_case"],
            "question_count": 0,
            "patient_answers": [],
        },
        config=config,
    )

    assert result["__interrupt__"][0].value["type"] == "patient_question"

    for answer in scenario["answers"]:
        result = await graph.ainvoke(
            Command(resume=answer),
            config=config,
        )

    assert result["question_count"] == 5
    assert len(result["patient_answers"]) == 5
    assert result["__interrupt__"][0].value["type"] == "physician_review"
    assert (
        result["interim_care"]["urgency"]
        == scenario["expected_urgency"]
    )

    physician_review = {
        "treatment": "Physician-approved course of action.",
        "notes": "Continue monitoring the patient.",
    }

    result = await graph.ainvoke(
        Command(resume=physician_review),
        config=config,
    )

    report = result["final_report"]

    assert result["next"] == "FINISH"
    assert report["physician_recommendation"] == physician_review["treatment"]
    assert report["physician_notes"] == physician_review["notes"]
    assert "does not replace" in report["disclaimer"]