import datetime
from app.extensions import db


class Project(db.Model):
    __tablename__ = "projects"
    __bind_key__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=True)
    summary = db.Column(db.String(300), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    link = db.Column(db.String(200), nullable=True)
    date = db.Column(db.Date, nullable=False)

    type = db.Column(db.Text, nullable=False)  # porject or event
    tags = db.Column(db.String(200))  # comma-separated
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<Project {self.id}: {self.title} ({self.type})>"
