from typing import Annotated, Literal
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

class MedicalState(TypedDict, total = False):
    messages: Annotated[list[AnyMessage], add_messages]

    initial_case: str

    next: Literal[
        "diagnostic_agent",
        "interim_care_agent",
        "physician_review",
        "report_agent",
        "FINISH"
    ]

    question_count: int
    current_question: str
    patient_answers: list[dict[str,str]]

    diagnostic_summary: dict[str, object]
    interim_care: dict[str, object]

    physician_treatment: str
    physician_notes: str

    final_report: dict[str, object]