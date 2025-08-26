import os
import json
from flask import Blueprint, jsonify, request, send_from_directory, abort, current_app
from ..models.clients import Client, Progress
from ..extensions import db
import datetime

bp = Blueprint("clients", __name__)

# ---- Регистрация ----
@bp.post("/clients/register")
def register():
    data = request.json
    email = data.get("email").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    if Client.query.filter_by(email=email).first():
        return jsonify({"error": "Пользователь уже существует"}), 409

    user = Client(email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"status": "registered", "email": email}), 201


# ---- Логин ----
@bp.post("/clients/login")
def login():
    data = request.json
    email = data.get("email").strip().lower()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = Client.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Неверный email или пароль"}), 404

    if user.password != password:
        return jsonify({"error": "Неверный email или пароль"}), 401

    return jsonify({"status": "ok", "email": user.email}), 200


# ---- Приём прогресса ----
@bp.post("/clients/progress")
def upload_progress():
    data = request.json
    email = data.get("email").strip().lower()
    prog = data.get("progress", {})

    user = Client.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # # Удаляем старый прогресс
    # Progress.query.filter_by(user_id=user.id).delete()

    # Записываем новый
    for word_id, rec in prog.items():
        record = Progress(
            user_id=user.id,
            word_id=word_id,
            memory_score=rec.get("memoryScore", 0),
            last_reviewed=datetime.datetime.utcfromtimestamp(rec["lastReviewed"]),
            swipe_up_count=rec.get("swipeUpCount", 0),
            swipe_down_count=rec.get("swipeDownCount", 0),
        )
        db.session.add(record)

    db.session.commit()
    return jsonify({"status": "progress saved"}), 200


# ---- Выдача прогресса ----
@bp.get("/clients/progress")
def fetch_progress():
    email = request.args.get("email").strip().lower()
    user = Client.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    result = {
        "email": email,
        "progress": {
            rec.word_id: {
                "id": rec.word_id,
                "memoryScore": rec.memory_score,
                "lastReviewed": rec.last_reviewed.timestamp(),
                "swipeUpCount": rec.swipe_up_count,
                "swipeDownCount": rec.swipe_down_count,
            }
            for rec in user.progress
        },
    }
    return jsonify(result), 200