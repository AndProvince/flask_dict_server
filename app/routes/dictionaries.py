import os
import json
from flask import Blueprint, jsonify, request, send_from_directory, abort, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.dictionary import Dictionary, DictionaryEntry
from ..models.meta import DictionariesMeta
from ..models.user import User

bp = Blueprint("dictionaries", __name__)

# Helpers

def get_global_meta():
    meta = DictionariesMeta.query.first()
    if not meta:
        meta = DictionariesMeta(version=0)
        db.session.add(meta)
        db.session.commit()
    return meta

def increment_global_meta():
    meta = DictionariesMeta.query.first()
    if not meta:
        meta = DictionariesMeta(version=0)

    meta.version += 1
    db.session.add(meta)
    db.session.commit()
    return meta


def dict_to_json_list(d: Dictionary):
    # Keep deterministic order by DB PK
    entries = sorted(d.entries, key=lambda e: e.id)
    out = []
    for e in entries:
        out.append({
            "id": e.entry_id,
            "englishWord": e.englishWord,
            "englishIPA": e.englishIPA or "",
            "englishIPAru": e.englishIPAru or "",
            "russianWord": e.russianWord or "",
            "russianIPA": e.russianIPA or "",
            "russianIPAen": e.russianIPAen or "",
            "level": e.level or d.level,
        })
    return out


def write_dictionary_file(d: Dictionary) -> str:
    data = dict_to_json_list(d)
    file_path = os.path.join(current_app.config["DICTIONARIES_DIR"], d.filename())
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True


def delete_dictionary_file(d: Dictionary) -> bool:
    """
    Удаляет файл словаря с диска.
    Возвращает True, если файл был найден и удалён, иначе False.
    """
    file_path = os.path.join(current_app.config["DICTIONARIES_DIR"], d.filename())
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False

# ---- Public listing ----
@bp.get("/version")
def list_dictionaries():
    dicts = Dictionary.query.filter_by(published=True).all()
    files = [
        {"language": d.language, "level": d.level, "url": f"/dictionary/{d.language}/{d.level}"}
        for d in sorted(dicts, key=lambda x: (x.language, x.level))
    ]
    meta = get_global_meta()
    return jsonify({"files": files, "version": meta.version_str()})


@bp.get("/dictionary/<lang>/<level>")
def get_dictionary(lang: str, level: str):
    d = Dictionary.query.filter_by(language=lang.upper(), level=level.upper(), published=True).first()
    if not d:
        abort(404, description="Dictionary not found")
    folder = current_app.config["DICTIONARIES_DIR"]
    file_path = os.path.join(folder, d.filename())
    if not os.path.exists(file_path):
        write_dictionary_file(d)
    return send_from_directory(folder, d.filename(), as_attachment=False)

