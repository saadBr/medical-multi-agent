from backend.app.state import MedicalState
from backend.app.tools.patient_tools import ask_patient


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

    summary = (
        f"Initial case: {state.get('initial_case', '')}\n"
        f"Patient responses:\n{answers_text}"
    )

    return {"diagnostic_summary": summary}