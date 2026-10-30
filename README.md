# Student Card OCR (FastAPI + RapidOCR)

    pip install -r requirements.txt
    uvicorn main:app --port 8000      # docs: http://127.0.0.1:8000/docs

    curl -F student_id=1156052 -F file=@card.jpg http://127.0.0.1:8000/card/verify

Config via env: STUDENT_ID_REGEX, CARD_KEYWORDS, MIN_KEYWORDS, MIN_ID_SCORE, CORS_ORIGINS.
Images are processed in memory and never stored.
