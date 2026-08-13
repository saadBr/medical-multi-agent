import httpx
import streamlit as st


API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Medical Multi-Agent System",
    page_icon="🩺",
    layout="centered",
)

st.title("Medical Multi-Agent System")
st.caption("Academic clinical-orientation workflow")

st.warning(
    "This system is an academic project and does not replace "
    "a medical consultation."
)

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "status" not in st.session_state:
    st.session_state.status = "not_started"

if "pending_interrupt" not in st.session_state:
    st.session_state.pending_interrupt = None


def start_consultation(initial_case: str):
    with httpx.Client(timeout=60) as client:
        session_response = client.post(f"{API_URL}/sessions/start")
        session_response.raise_for_status()

        thread_id = session_response.json()["thread_id"]

        consultation_response = client.post(
            f"{API_URL}/consultation/start",
            json={
                "thread_id": thread_id,
                "initial_case": initial_case,
            },
        )
        consultation_response.raise_for_status()

    data = consultation_response.json()

    st.session_state.thread_id = thread_id
    st.session_state.status = data["status"]
    st.session_state.pending_interrupt = data["pending_interrupt"]

def resume_consultation(response):
    with httpx.Client(timeout=60) as client:
        api_response = client.post(
            f"{API_URL}/consultation/resume",
            json={
                "thread_id": st.session_state.thread_id,
                "response": response,
            },
        )
        api_response.raise_for_status()

    data = api_response.json()

    st.session_state.status = data["status"]
    st.session_state.pending_interrupt = data["pending_interrupt"]

def get_final_report() -> str:
    with httpx.Client(timeout=60) as client:
        response = client.get(
            f"{API_URL}/consultation/"
            f"{st.session_state.thread_id}/report"
        )
        response.raise_for_status()

    return response.json()["report"]


if st.session_state.status == "not_started":
    st.subheader("Start a consultation")

    initial_case = st.text_area(
        "Describe the patient's initial case",
        placeholder=(
            "Example: The patient reports a cough and fever "
            "for two days."
        ),
    )

    if st.button("Start consultation", type="primary"):
        if len(initial_case.strip()) < 10:
            st.error("Please provide a more detailed initial case.")
        else:
            try:
                start_consultation(initial_case.strip())
                st.rerun()
            except httpx.HTTPError as error:
                st.error(f"Could not start consultation: {error}")

elif st.session_state.status == "waiting_for_patient":
    st.subheader("Patient questions")

    pending = st.session_state.pending_interrupt
    st.info(pending["question"])

    with st.form("patient_answer_form", clear_on_submit=True):
        answer = st.text_area("Your answer")
        submitted = st.form_submit_button(
            "Submit answer",
            type="primary",
        )

    if submitted:
        if not answer.strip():
            st.error("Please provide an answer.")
        else:
            try:
                resume_consultation(answer.strip())
                st.rerun()
            except httpx.HTTPError as error:
                st.error(f"Could not submit answer: {error}")

    st.caption(f"Consultation ID: {st.session_state.thread_id}")

elif st.session_state.status == "waiting_for_physician":
    st.subheader("Physician review")

    pending = st.session_state.pending_interrupt

    st.markdown("#### Preliminary clinical summary")
    st.json(pending["diagnostic_summary"])

    st.markdown("#### Interim care recommendation")
    st.json(pending["interim_care"])

    with st.form("physician_review_form"):
        treatment = st.text_area(
            "Treatment or recommended course of action"
        )
        notes = st.text_area("Additional physician notes")

        submitted = st.form_submit_button(
            "Submit physician review",
            type="primary",
        )

    if submitted:
        if not treatment.strip():
            st.error(
                "Please provide a treatment or recommended course of action."
            )
        else:
            try:
                resume_consultation(
                    {
                        "treatment": treatment.strip(),
                        "notes": notes.strip(),
                    }
                )
                st.rerun()
            except httpx.HTTPError as error:
                st.error(f"Could not submit review: {error}")

    st.caption(f"Consultation ID: {st.session_state.thread_id}")

elif st.session_state.status == "completed":
    st.subheader("Final medical orientation report")

    try:
        report = get_final_report()
        st.text(report)
    except httpx.HTTPError as error:
        st.error(f"Could not retrieve the report: {error}")

    st.caption(f"Consultation ID: {st.session_state.thread_id}")

    if st.button("Start a new consultation"):
        st.session_state.thread_id = None
        st.session_state.status = "not_started"
        st.session_state.pending_interrupt = None
        st.rerun()