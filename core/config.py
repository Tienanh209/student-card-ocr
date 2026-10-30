import os

from dotenv import load_dotenv

load_dotenv()

# Student ID format. YZU IDs in the sample are 7 digits; override via env if needed.
STUDENT_ID_REGEX = os.getenv("STUDENT_ID_REGEX", r"(?<!\d)\d{7}(?!\d)")

# Text that must appear on a card (normalized: no spaces, upper-case).
CARD_KEYWORDS = tuple(
    k.strip().upper()
    for k in os.getenv(
        "CARD_KEYWORDS", "元智大學,學生證,STUDENTIDCARD,YUANZEUNIVERSITY,YUANZE,學號"
    ).split(",")
)
MIN_KEYWORDS = int(os.getenv("MIN_KEYWORDS", "2"))

# Label printed next to the ID (used to pick the right number on the card).
ID_LABELS = ("學號", "学号")

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(8 * 1024 * 1024)))
MAX_IMAGE_SIDE = int(os.getenv("MAX_IMAGE_SIDE", "1600"))

# Below this OCR score the ID is reported as "unreliable" -> ask user to retake.
MIN_ID_SCORE = float(os.getenv("MIN_ID_SCORE", "0.80"))

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
