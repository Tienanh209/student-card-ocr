from __future__ import annotations

import re
import time
from dataclasses import dataclass

import cv2
import numpy as np

from core import config
from core.errors import InvalidStudentIdError
from models.ocr_engine import OCRItem, RapidOCREngine

_ID_RE = re.compile(config.STUDENT_ID_REGEX)

# (angle label, cv2 rotate code). Try upright first, then the sideways cases.
_ROTATIONS: list[tuple[int, int | None]] = [
    (0, None),
    (90, cv2.ROTATE_90_CLOCKWISE),
    (270, cv2.ROTATE_90_COUNTERCLOCKWISE),
    (180, cv2.ROTATE_180),
]


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text).upper()


def _center(box: list[list[float]]) -> tuple[float, float]:
    xs = [p[0] for p in box]
    ys = [p[1] for p in box]
    return sum(xs) / len(xs), sum(ys) / len(ys)


@dataclass
class ScanResult:
    is_student_card: bool
    card_score: int
    detected_id: str | None
    id_confidence: float | None
    rotation_deg: int
    elapsed_ms: float


class CardService:
    def __init__(self, engine: RapidOCREngine) -> None:
        self.engine = engine

    # ---------- public API ----------
    def scan(self, image: np.ndarray) -> ScanResult:
        t0 = time.perf_counter()
        best: tuple[int, int, list[OCRItem]] | None = None  # (score, angle, items)

        for angle, code in _ROTATIONS:
            im = image if code is None else cv2.rotate(image, code)
            items = self.engine.run(im)
            score = self._card_score(items)
            if best is None or score > best[0]:
                best = (score, angle, items)
            if score >= config.MIN_KEYWORDS:
                break  # found the right orientation, stop early

        score, angle, items = best  # type: ignore[misc]
        is_card = score >= config.MIN_KEYWORDS
        student_id, conf = self._extract_id(items) if is_card else (None, None)
        return ScanResult(
            is_student_card=is_card,
            card_score=score,
            detected_id=student_id,
            id_confidence=conf,
            rotation_deg=angle,
            elapsed_ms=round((time.perf_counter() - t0) * 1000, 2),
        )

    def verify(self, image: np.ndarray, claimed_id: str) -> tuple[ScanResult, str]:
        claimed = claimed_id.strip()
        if not _ID_RE.fullmatch(claimed):
            raise InvalidStudentIdError("Student ID format is invalid")

        res = self.scan(image)
        if not res.is_student_card:
            return res, "NOT_A_STUDENT_CARD"
        if res.detected_id is None:
            return res, "ID_NOT_READABLE"
        if (res.id_confidence or 0) < config.MIN_ID_SCORE:
            return res, "ID_LOW_CONFIDENCE"
        if res.detected_id != claimed:
            return res, "ID_MISMATCH"
        return res, "OK"

    # ---------- internals ----------
    @staticmethod
    def _card_score(items: list[OCRItem]) -> int:
        joined = _norm("".join(i.text for i in items))
        return sum(1 for k in config.CARD_KEYWORDS if k in joined)

    @staticmethod
    def _extract_id(items: list[OCRItem]) -> tuple[str | None, float | None]:
        """Pick the ID number closest to the 學號 label; fall back to any match."""
        candidates: list[tuple[str, float, tuple[float, float]]] = []
        label_pos: tuple[float, float] | None = None

        for it in items:
            t = _norm(it.text)
            if any(lbl in t for lbl in config.ID_LABELS):
                label_pos = _center(it.box)
            m = _ID_RE.search(t)
            if m:
                candidates.append((m.group(), it.score, _center(it.box)))

        if not candidates:
            return None, None
        if label_pos is not None:
            candidates.sort(
                key=lambda c: (c[2][0] - label_pos[0]) ** 2 + (c[2][1] - label_pos[1]) ** 2
            )
        value, score, _ = candidates[0]
        return value, round(score, 4)
