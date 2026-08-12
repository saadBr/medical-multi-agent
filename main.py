from backend.app.graph import graph
from langgraph.types import Command

def main():
    config = {
        "configurable": {
            "thread_id": "test-consultation-1",
        }
    }

    initial_state = {
        "initial_case": (
            "The patient reports a cough, mild fever, and fatigue "
            "for the last two days."
        ),
        "question_count": 0,
        "patient_answers": [],
    }

    result = graph.invoke(initial_state, config=config)

    while result.get("__interrupt__"):
        interruption = result["__interrupt__"][0]
        payload = interruption.value

        if payload["type"] == "patient_question":
            print(f"\nQuestion: {payload['question']}")
            response = input("Your answer: ")

        elif payload["type"] == "physician_review":
            print("\n--- PHYSICIAN REVIEW ---")
            print(payload["diagnostic_summary"])

            treatment = input("\nTreatment or course of action: ")
            notes = input("Additional physician notes: ")

            response = {
                "treatment": treatment,
                "notes": notes,
            }

        else:
            raise ValueError(f"Unknown interruption type: {payload['type']}")

        result = graph.invoke(
            Command(resume=response),
            config=config,
        )

    print("\n" + result["final_report"])


if __name__ == "__main__":
    main()