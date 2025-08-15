from ..extensions import db


class DictionariesMeta(db.Model):
    __bind_key__ = "dicts"
    __tablename__ = "dictionaries_meta"

    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer, default=0, nullable=False)

    def version_str(self) -> str:
        return format_number(self.version)

def format_number(num):
    s = str(num).zfill(6)
    # Разбиваем справа на пары
    parts = []
    while s:
        parts.insert(0, s[-2:])
        s = s[:-2]
    return ".".join(parts)

