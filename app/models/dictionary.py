from datetime import datetime
from ..extensions import db


class Dictionary(db.Model):
    __bind_key__ = "dicts"
    __tablename__ = "dictionaries"

    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(10), nullable=False)
    level = db.Column(db.String(10), nullable=False)
    version_major = db.Column(db.Integer, default=0, nullable=False)
    version_minor = db.Column(db.Integer, default=0, nullable=False)
    version_patch = db.Column(db.Integer, default=0, nullable=False)
    published = db.Column(db.Boolean, default=False)
    owner_id = db.Column(db.Integer, nullable=True)  # logical link to users.users.id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entries = db.relationship(
        "DictionaryEntry",
        backref="dictionary",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    __table_args__ = (
        db.UniqueConstraint("language", "level", name="_lang_level_uc"),
    )

    def version_str(self) -> str:
        return f"{self.version_major}.{self.version_minor:02d}.{self.version_patch:02d}"

    def filename(self) -> str:
        return f"{self.language}_{self.level}_words_full.json"


class DictionaryEntry(db.Model):
    __bind_key__ = "dicts"
    __tablename__ = "dictionary_entries"

    id = db.Column(db.Integer, primary_key=True)
    dictionary_id = db.Column(
        db.Integer, db.ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False
    )

    # exact schema fields
    entry_id = db.Column(db.String(50), nullable=False, index=True)  # e.g., "b1_0001"
    englishWord = db.Column(db.String(255), nullable=False)
    englishIPA = db.Column(db.String(255))
    englishIPAru = db.Column(db.String(255))
    russianWord = db.Column(db.String(255))
    russianIPA = db.Column(db.String(255))
    russianIPAen = db.Column(db.String(255))
    level = db.Column(db.String(10))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)