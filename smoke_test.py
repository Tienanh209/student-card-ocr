"""Smoke test: run the real API on the sample card + error branches."""
import sys

from fastapi.testclient import TestClient

from main import app

IMG = sys.argv[1]
ID = sys.argv[2]

with TestClient(app) as c:
    print("health", c.get("/health").json())
    data = open(IMG, "rb").read()

    r = c.post("/card/scan", files={"file": ("card.jpg", data, "image/jpeg")})
    print("scan", r.status_code, r.json())

    r = c.post("/card/verify", data={"student_id": ID}, files={"file": ("card.jpg", data, "image/jpeg")})
    print("verify(correct)", r.status_code, r.json())

    wrong = "1156053" if ID != "1156053" else "1156054"
    r = c.post("/card/verify", data={"student_id": wrong}, files={"file": ("card.jpg", data, "image/jpeg")})
    print("verify(wrong)", r.status_code, r.json()["reason"])

    r = c.post("/card/verify", data={"student_id": "abc"}, files={"file": ("card.jpg", data, "image/jpeg")})
    print("verify(bad format)", r.status_code, r.json())

    r = c.post("/card/verify", data={"student_id": ID}, files={"file": ("x.jpg", b"notanimage", "image/jpeg")})
    print("verify(not image)", r.status_code, r.json())

    r = c.post("/card/verify", data={"student_id": ID}, files={"file": ("x.jpg", b"", "image/jpeg")})
    print("verify(empty)", r.status_code, r.json())

    r = c.post("/card/verify", data={"student_id": ID})
    print("verify(no file)", r.status_code, r.json()["error"]["code"])

    r = c.get("/nope")
    print("404", r.status_code, r.json())
