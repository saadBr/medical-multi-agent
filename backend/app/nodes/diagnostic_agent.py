from backend.app.state import MedicalState
from backend.app.tools.patient_tools import ask_patient

from langchain_core.messages import HumanMessage, SystemMessage

from backend.app.llm import llm
from backend.app.schemas import ClinicalSummary

QUESTIONS = [
    "When did your symptoms begin?",
    "How severe are your symptoms on a scale from 1 to 10?",
    "Do you have any other symptoms?",
    "Do you have any relevant medical conditions or allergies?",
    "Have your symptoms worsened, or are you experiencing any warning signs?",
]


def diagnostic_agent(state: MedicalState) -> dict:
    """Ask five successive questions, then produce a preliminary summary."""

    question_count = state.get("question_count", 0)

    if question_count < len(QUESTIONS):
        question = QUESTIONS[question_count]
        answer = ask_patient.invoke({"question": question})

        updated_answers = [
            *state.get("patient_answers", []),
            {
                "question": question,
                "answer": answer,
            },
        ]

        return {
            "current_question": question,
            "patient_answers": updated_answers,
            "question_count": question_count + 1,
        }

    answers_text = "\n".join(
        f"- {item['question']} {item['answer']}"
        for item in state.get("patient_answers", [])
    )
    structured_llm = llm.with_structured_output(ClinicalSummary)

    summary = structured_llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are part of an academic clinical-orientation system. "
                    "Create only a cautious preliminary clinical summary. "
                    "Do not provide a definitive diagnosis. "
                    "Use only information explicitly provided by the patient. "
                    "Do not invent symptoms, history, allergies, or warning signs."
                    "Only include positively reported warning signs in warning_signs. "
                    "Never include symptoms that the patient explicitly denied. "
                    "Only include positively reported conditions or allergies in relevant_history. "
                    "Return an empty list when the patient reports none. "
                )
            ),
            HumanMessage(
                content=(
                    f"Initial case:\n{state.get('initial_case', '')}\n\n"
                    f"Patient responses:\n{answers_text}"
                )
            ),
        ]
    )

    return {"diagnostic_summary": summary.model_dump(),}