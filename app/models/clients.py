from app.extensions import db
import datetime

# --------- Модели ---------
class Client(db.Model):
    __bind_key__ = "dicts"
    __tablename__ = "clients"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    # Каскадное удаление прогресса
    progress = db.relationship(
        "Progress",
        backref="client",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Progress(db.Model):
    __bind_key__ = "dicts"
    __tablename__ = "progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("clients.id", ondelete="CASCADE"), nullable=False)
    word_id = db.Column(db.String, nullable=False)
    memory_score = db.Column(db.Integer, nullable=False)
    last_reviewed = db.Column(db.DateTime, nullable=False)
    swipe_up_count = db.Column(db.Integer, default=0)
    swipe_down_count = db.Column(db.Integer, default=0)