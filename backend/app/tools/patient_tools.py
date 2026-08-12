from langchain_core.tools import tool
from langgraph.types import interrupt

@tool
def ask_patient(question:str)->str:
    """Ask the patient one question and pause until an answer is provided."""
    answer = interrupt(
        {
            "type": "patient_question",
            "question": question,
        }
    )

    return str(answer)