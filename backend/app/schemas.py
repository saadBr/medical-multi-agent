from typing import Literal

from pydantic import BaseModel, Field


class ClinicalSummary(BaseModel):
    main_complaint: str = Field(
        description="The patient's primary reported concern."
    )
    symptoms: list[str] = Field(
        description="Symptoms explicitly reported by the patient."
    )
    duration: str = Field(
        description="Reported duration of the symptoms."
    )
    severity: Literal["low", "moderate", "high"] = Field(
        description="Preliminary severity based only on provided information."
    )
    relevant_history: list[str] = Field(
        description=(
        "Only medical conditions or allergies positively reported by the patient. "
        "Exclude statements indicating none are known. "
        "Return an empty list when no relevant history is reported."
    )
    )
    warning_signs: list[str] = Field(
        description=(
            "Only warning signs positively reported by the patient. "
            "Exclude denied or absent symptoms such as 'no chest pain'. "
            "Return an empty list when no warning signs are present."
        )
    )
    preliminary_orientation: str = Field(
        description="A cautious preliminary clinical orientation, not a diagnosis."
    )
class SessionResponse(BaseModel):
    thread_id: str


class ConsultationStartRequest(BaseModel):
    thread_id: str
    initial_case: str = Field(min_length=10)


class PhysicianReviewInput(BaseModel):
    treatment: str = Field(min_length=1)
    notes: str = ""


class ConsultationResumeRequest(BaseModel):
    thread_id: str
    response: str | PhysicianReviewInput

class FinalReport(BaseModel):
    title: str = "Final Medical Orientation Report"
    initial_case: str
    preliminary_summary: ClinicalSummary
    interim_care: dict[str, object]
    physician_recommendation: str
    physician_notes: str
    disclaimer: str