import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core import config
from core.errors import ServiceError
from models.ocr_engine import RapidOCREngine
from routers import card
from services.card_service import CardService

log = logging.getLogger("student-card-ocr")


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = RapidOCREngine()
    engine.load()  # once, at startup (single small model -> no lazy registry needed)
    app.state.engine = engine
    app.state.card_service = CardService(engine)
    log.info("OCR engine loaded")
    yield
    engine.unload()


app = FastAPI(title="Student Card OCR", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=config.CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"]
)
app.include_router(card.router)


@app.get("/health", tags=["system"])
def health(request: Request):
    return {"status": "ok", "model_loaded": request.app.state.engine.is_loaded}


def _err(status: int, code: str, message: str, details=None) -> JSONResponse:
    body = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return JSONResponse(status_code=status, content=body)


@app.exception_handler(ServiceError)
async def service_error_handler(request: Request, exc: ServiceError):
    if exc.status_code >= 500:
        log.exception("service error", exc_info=exc)
    return _err(exc.status_code, exc.code, str(exc))


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return _err(422, "VALIDATION_ERROR", "Request is invalid", jsonable(exc.errors()))


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException):
    return _err(exc.status_code, f"HTTP_{exc.status_code}", str(exc.detail))


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    log.exception("unhandled error", exc_info=exc)
    return _err(500, "INTERNAL_ERROR", "Internal server error")


def jsonable(errors):
    # pydantic errors may contain non-serializable ctx; strip to simple fields
    return [{"loc": list(e.get("loc", [])), "type": e.get("type"), "msg": e.get("msg")} for e in errors]
