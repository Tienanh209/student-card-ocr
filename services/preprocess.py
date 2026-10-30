import cv2
import numpy as np

from core import config
from core.errors import EmptyFileError, ImageDecodeError, ImageTooLargeError


def load_image_from_bytes(data: bytes) -> np.ndarray:
    if not data:
        raise EmptyFileError("Uploaded file is empty")
    if len(data) > config.MAX_UPLOAD_BYTES:
        raise ImageTooLargeError(
            f"File exceeds {config.MAX_UPLOAD_BYTES // (1024 * 1024)} MB limit"
        )
    img = cv2.imdecode(np.frombuffer(data, np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise ImageDecodeError("File is not a valid image")
    return limit_side(img, config.MAX_IMAGE_SIDE)


def limit_side(img: np.ndarray, max_side: int) -> np.ndarray:
    h, w = img.shape[:2]
    scale = max_side / max(h, w)
    if scale >= 1:
        return img
    return cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
