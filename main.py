from backend.app.graph import graph


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

    print(result["final_report"])


if __name__ == "__main__":
    main()