from __future__ import annotations

import base64
import os
from pathlib import Path

import cv2
import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS

from emotion_camera import (
    EMOTION_LABELS,
    classify_emotion,
    detect_faces,
    ensure_model,
    load_emotion_session,
    load_face_detector,
    padded_face_region,
    rebalance_probabilities,
    resolve_emotion_label,
)

app = Flask(__name__)
CORS(app)

# Load once at startup so requests are fast.
MODEL_PATH = ensure_model(Path("models/emotion-ferplus-8.onnx"))
DETECTOR = load_face_detector()
SESSION = load_emotion_session(MODEL_PATH)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.post("/detect")
def detect():
    payload = request.get_json(silent=True) or {}
    frame_data = payload.get("frame")
    if not isinstance(frame_data, str) or not frame_data:
        return jsonify({"error": "Missing frame"}), 400

    if "," in frame_data:
        frame_data = frame_data.split(",", 1)[1]

    try:
        binary = base64.b64decode(frame_data)
    except Exception:
        return jsonify({"error": "Invalid base64 frame"}), 400

    arr = np.frombuffer(binary, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        return jsonify({"error": "Cannot decode image"}), 400

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detect_faces(DETECTOR, gray, min_face=48)
    if len(faces) == 0:
        return jsonify(
            {
                "dominant_emotion": "no_face",
                "confidence": 0.0,
                "all_probabilities": {label: 0.0 for label in EMOTION_LABELS},
            }
        )

    x, y, w, h = max(faces, key=lambda box: box[2] * box[3])
    face_region = padded_face_region(gray, (x, y, w, h), padding=0.22)
    _, probabilities = classify_emotion(
        SESSION,
        face_region,
        neutral_penalty=0.5,
        emotion_boost=1.3,
    )

    calibrated = rebalance_probabilities(probabilities, neutral_cap=0.40)
    _, best_idx, confidence, should_count = resolve_emotion_label(
        calibrated,
        confidence_threshold=0.55,
        expressive_margin=0.14,
    )

    result = {
        "dominant_emotion": EMOTION_LABELS[best_idx] if should_count else "uncertain",
        "confidence": float(confidence),
        "all_probabilities": {
            label: float(calibrated[i]) for i, label in enumerate(EMOTION_LABELS)
        },
    }
    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
