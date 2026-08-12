from fastapi import FastAPI, HTTPException
from backend.app.graph import graph
from backend.app.schemas import ConsultationStartRequest
from uuid import uuid4
from langgraph.types import Command
from backend.app.schemas import ConsultationResumeRequest
from backend.app.schemas import SessionResponse

app = FastAPI(
    title="Medical Multi-Agent API",
    description="Academic clinical-orientation workflow using LangGraph.",
    version="0.1.0",
)

sessions: set[str] = set()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/sessions/start", response_model=SessionResponse)
async def start_session():
    thread_id = str(uuid4())
    sessions.add(thread_id)

    return SessionResponse(thread_id=thread_id)

@app.post("/consultation/start")
async def start_consultation(request: ConsultationStartRequest):
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    result = await graph.ainvoke(
        {
            "initial_case": request.initial_case,
            "question_count": 0,
            "patient_answers": [],
        },
        config=config,
    )

    interruption = result["__interrupt__"][0].value

    return {
        "thread_id": request.thread_id,
        "status": "waiting_for_patient",
        "pending_interrupt": interruption,
    }

@app.post("/consultation/resume")
async def resume_consultation(request: ConsultationResumeRequest):
    if request.thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    config = {
        "configurable": {
            "thread_id": request.thread_id,
        }
    }

    response = request.response

    if hasattr(response, "model_dump"):
        response = response.model_dump()

    result = await graph.ainvoke(
        Command(resume=response),
        config=config,
    )

    interruptions = result.get("__interrupt__", [])

    if interruptions:
        pending = interruptions[0].value
        status = (
            "waiting_for_patient"
            if pending["type"] == "patient_question"
            else "waiting_for_physician"
        )

        return {
            "thread_id": request.thread_id,
            "status": status,
            "pending_interrupt": pending,
        }

    return {
        "thread_id": request.thread_id,
        "status": "completed",
        "pending_interrupt": None,
    }

@app.get("/consultation/{thread_id}")
async def get_consultation(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    snapshot = await graph.aget_state(config)

    if not snapshot.values:
        raise HTTPException(
            status_code=404,
            detail="Consultation has not been started.",
        )

    pending_interrupt = None

    for task in snapshot.tasks:
        if task.interrupts:
            pending_interrupt = task.interrupts[0].value
            break

    if pending_interrupt:
        status = (
            "waiting_for_patient"
            if pending_interrupt["type"] == "patient_question"
            else "waiting_for_physician"
        )
    elif snapshot.values.get("final_report"):
        status = "completed"
    else:
        status = "processing"

    return {
        "thread_id": thread_id,
        "status": status,
        "state": snapshot.values,
        "pending_interrupt": pending_interrupt,
    }

@app.get("/consultation/{thread_id}/report")
async def get_consultation_report(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found.")

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    snapshot = await graph.aget_state(config)
    final_report = snapshot.values.get("final_report")

    if not final_report:
        raise HTTPException(
            status_code=409,
            detail="The final report is not available yet.",
        )

    return {
        "thread_id": thread_id,
        "report": final_report,
    }