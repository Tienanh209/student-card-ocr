from fastapi import APIRouter, Depends, File, Form, Request, UploadFile
from fastapi.concurrency import run_in_threadpool

from schemas.card import ErrorResponse, ScanResponse, VerifyResponse
from services.card_service import CardService
from services.preprocess import load_image_from_bytes

router = APIRouter(prefix="/card", tags=["student-card"])


def get_service(request: Request) -> CardService:
    return request.app.state.card_service


_ERRORS = {400: {"model": ErrorResponse}, 413: {"model": ErrorResponse},
           422: {"model": ErrorResponse}, 503: {"model": ErrorResponse}}


@router.post("/verify", response_model=VerifyResponse, responses=_ERRORS)
async def verify_card(
    student_id: str = Form(..., min_length=1, max_length=20, description="ID the student typed"),
    file: UploadFile = File(..., description="Photo of the student card"),
    service: CardService = Depends(get_service),
):
    image = load_image_from_bytes(await file.read())
    res, reason = await run_in_threadpool(service.verify, image, student_id)
    return VerifyResponse(
        verified=reason == "OK",
        reason=reason,
        is_student_card=res.is_student_card,
        card_score=res.card_score,
        detected_id=res.detected_id,
        id_confidence=res.id_confidence,
        rotation_deg=res.rotation_deg,
        elapsed_ms=res.elapsed_ms,
    )


@router.post("/scan", response_model=ScanResponse, responses=_ERRORS)
async def scan_card(
    file: UploadFile = File(...),
    service: CardService = Depends(get_service),
):
    """Detect card + read ID without comparing (useful for debugging/tuning)."""
    image = load_image_from_bytes(await file.read())
    res = await run_in_threadpool(service.scan, image)
    return ScanResponse(**res.__dict__)
