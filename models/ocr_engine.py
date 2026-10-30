from __future__ import annotations

import threading
from dataclasses import dataclass

import numpy as np

from core.errors import ModelBackendError


@dataclass
class OCRItem:
    text: str
    score: float
    box: list[list[float]]  # 4 points [[x,y], ...]


class RapidOCREngine:
    """Thin wrapper around RapidOCR (ONNX, CPU). Loaded once at startup."""

    def __init__(self) -> None:
        self._ocr = None
        self._lock = threading.Lock()

    @property
    def is_loaded(self) -> bool:
        return self._ocr is not None

    def load(self) -> None:
        with self._lock:
            if self._ocr is None:
                try:  # new package (Python 3.13+): rapidocr
                    from rapidocr import RapidOCR
                except ImportError:  # legacy package: rapidocr-onnxruntime
                    from rapidocr_onnxruntime import RapidOCR

                self._ocr = RapidOCR()

    def unload(self) -> None:
        with self._lock:
            self._ocr = None

    def run(self, image: np.ndarray) -> list[OCRItem]:
        if self._ocr is None:
            raise ModelBackendError("OCR model is not loaded")
        try:
            out = self._ocr(image)
        except Exception as exc:  # backend failure -> 503, details stay in logs
            raise ModelBackendError("OCR backend failed") from exc

        items: list[OCRItem] = []
        if hasattr(out, "txts"):  # new rapidocr: RapidOCROutput
            if out.txts is None:
                return items
            for box, text, score in zip(out.boxes, out.txts, out.scores):
                items.append(OCRItem(str(text), float(score), [list(map(float, p)) for p in box]))
        else:  # legacy: (result, elapse) with result = [[box, text, score], ...]
            result = out[0] if isinstance(out, tuple) else out
            for box, text, score in result or []:
                items.append(OCRItem(str(text), float(score), box))
        return items
