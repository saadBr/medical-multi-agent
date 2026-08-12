import asyncio

from langgraph.types import Command

from backend.app.graph import graph


async def main():
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

    result = await graph.ainvoke(initial_state, config=config)

    while result.get("__interrupt__"):
        payload = result["__interrupt__"][0].value

        if payload["type"] == "patient_question":
            print(f"\nQuestion: {payload['question']}")
            response = input("Your answer: ")

        elif payload["type"] == "physician_review":
            print("\n--- PHYSICIAN REVIEW ---")
            print("Clinical summary:")
            print(payload["diagnostic_summary"])
            print("\nMCP interim care:")
            print(payload["interim_care"])

            treatment = input("\nTreatment or course of action: ")
            notes = input("Additional physician notes: ")

            response = {
                "treatment": treatment,
                "notes": notes,
            }

        else:
            raise ValueError(
                f"Unknown interruption type: {payload['type']}"
            )

        result = await graph.ainvoke(
            Command(resume=response),
            config=config,
        )

    print("\n" + result["final_report"])


if __name__ == "__main__":
    asyncio.run(main())