from typing import Literal

from pydantic import BaseModel, Field

Reason = Literal[
    "OK",
    "NOT_A_STUDENT_CARD",
    "ID_NOT_READABLE",
    "ID_LOW_CONFIDENCE",
    "ID_MISMATCH",
]


class VerifyResponse(BaseModel):
    verified: bool
    reason: Reason
    is_student_card: bool
    card_score: int = Field(..., description="Number of card keywords found")
    detected_id: str | None = None
    id_confidence: float | None = Field(None, ge=0, le=1)
    rotation_deg: int = Field(0, description="Clockwise rotation applied to read the card")
    elapsed_ms: float


class ScanResponse(BaseModel):
    is_student_card: bool
    card_score: int
    detected_id: str | None = None
    id_confidence: float | None = Field(None, ge=0, le=1)
    rotation_deg: int = 0
    elapsed_ms: float


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[dict] | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
