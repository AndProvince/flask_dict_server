from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.dictionary import Dictionary, DictionaryEntry
from ..models.user import User
import json
from .dictionaries import write_dictionary_file, delete_dictionary_file, get_global_meta, increment_global_meta
from datetime import datetime

bp = Blueprint("ui", __name__, url_prefix="/dictionary")


# --- UI dictionary pages ---
@bp.get("/")
def index():
    return render_template("index.html")

@bp.context_processor
def inject_year():
    return {'current_year': datetime.utcnow().year}

@bp.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html")


@bp.get("/dashboard")
def dashboard():
    dicts = Dictionary.query.all()
    version = get_global_meta().version_str()
    return render_template("dictionary_list.html", dictionaries=dicts, version=version)


@bp.get("/new")
def new_dictionary_page():
    return render_template("dictionary_edit.html", dictionary=None)


@bp.post("/new")
@jwt_required()
def create_dictionary_ui():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    lang = (request.form.get("language") or "").strip().upper()
    level = (request.form.get("level") or "").strip().upper()
    if not lang or not level:
        flash("Заполните язык и уровень", "danger")
        return redirect(url_for("ui.new_dictionary_page"))

    if Dictionary.query.filter_by(language=lang, level=level).first():
        flash("Такой словарь уже существует", "danger")
        return redirect(url_for("ui.new_dictionary_page"))

    d = Dictionary(language=lang, level=level, owner_id=user_id)
    db.session.add(d)
    db.session.commit()
    flash("Словарь создан", "success")
    return redirect(url_for("ui.edit_dictionary", dict_id=d.id))


@bp.get("/<int:dict_id>/edit")
@jwt_required()
def edit_dictionary(dict_id: int):
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    d = Dictionary.query.get_or_404(dict_id)
    entries = DictionaryEntry.query.filter_by(dictionary_id=d.id).order_by(DictionaryEntry.id.asc()).all()
    return render_template("dictionary_edit.html", dictionary=d, entries=entries)


@bp.route("/<int:dict_id>/upload_json", methods=["GET", "POST"])
@jwt_required()
def upload_json(dict_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    d = Dictionary.query.get_or_404(dict_id)

    if request.method == "POST":
        file = request.files.get("json_file")

        if not file or not file.filename.endswith(".json"):
            flash("Загрузите корректный JSON-файл", "danger")
            return redirect(url_for("ui.upload_json", dict_id=dict_id))

        try:
            data = json.load(file)
        except Exception as e:
            flash(f"Ошибка чтения JSON: {e}", "danger")
            return redirect(url_for("ui.upload_json", dict_id=dict_id))

        added, skipped = 0, 0
        for item in data:
            # проверка обязательных полей
            if not all(k in item for k in ["id", "englishWord", "russianWord", "level"]):
                skipped += 1
                continue

            # проверка на дубликат по entry_id
            if DictionaryEntry.query.filter_by(dictionary_id=d.id, entry_id=item["id"]).first():
                skipped += 1
                continue

            entry = DictionaryEntry(
                dictionary_id=d.id,
                entry_id=item["id"],
                englishWord=item.get("englishWord"),
                englishIPA=item.get("englishIPA"),
                englishIPAru=item.get("englishIPAru"),
                russianWord=item.get("russianWord"),
                russianIPA=item.get("russianIPA"),
                russianIPAen=item.get("russianIPAen"),
                level=item.get("level"),
            )
            db.session.add(entry)
            added += 1

        db.session.commit()
        flash(f"Загружено {added} слов, пропущено {skipped}", "success")
        return redirect(url_for("ui.edit_dictionary", dict_id=dict_id))

    return render_template("upload_json.html", dictionary=d)


@bp.route("/<int:dict_id>/delete", methods=["POST"])
@jwt_required()
def delete_dictionary(dict_id):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        flash("Нет прав на удаление словарей", "danger")
        return redirect(url_for("ui.dashboard"))

    d = Dictionary.query.get_or_404(dict_id)
    db.session.delete(d)
    db.session.commit()

    flash(f"Словарь ID {dict_id} удалён", "success")
    return redirect(url_for("ui.dashboard"))


@bp.post("/<int:dict_id>/entry")
@jwt_required()
def add_entry_ui(dict_id: int):
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    d = Dictionary.query.get_or_404(dict_id)

    entry_id = (request.form.get("entry_id") or "").strip()
    english_word = (request.form.get("englishWord") or "").strip()
    english_ipa = (request.form.get("englishIPA") or "").strip()
    english_ipa_ru = (request.form.get("englishIPAru") or "").strip()
    russian_word = (request.form.get("russianWord") or "").strip()
    russian_ipa = (request.form.get("russianIPA") or "").strip()
    russian_ipa_en = (request.form.get("russianIPAen") or "").strip()
    level = (request.form.get("level") or "").strip()

    if not entry_id or not english_word or not russian_word or not level:
        flash("Заполните обязательные поля", "danger")
        return redirect(url_for("ui.edit_dictionary", dict_id=dict_id))

    if DictionaryEntry.query.filter_by(dictionary_id=d.id, entry_id=entry_id).first():
        flash("Запись с таким id уже есть", "danger")
        return redirect(url_for("ui.edit_dictionary", dict_id=dict_id))

    e = DictionaryEntry(
        dictionary_id=d.id,
        entry_id=entry_id,
        englishWord=english_word,
        englishIPA=english_ipa,
        englishIPAru=english_ipa_ru,
        russianWord=russian_word,
        russianIPA=russian_ipa,
        russianIPAen=russian_ipa_en,
        level=level,
    )
    db.session.add(e)
    db.session.commit()
    flash("Слово добавлено", "success")
    return redirect(url_for("ui.edit_dictionary", dict_id=dict_id))


@bp.post("/<int:dict_id>/entry/<int:entry_db_id>/update")
@jwt_required()
def edit_entry_ui(dict_id: int, entry_db_id: int):
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    d = Dictionary.query.get_or_404(dict_id)
    e = DictionaryEntry.query.filter_by(id=entry_db_id, dictionary_id=d.id).first_or_404()

    e.entry_id = (request.form.get("entry_id") or "").strip()
    e.englishWord = (request.form.get("englishWord") or "").strip()
    e.englishIPA = (request.form.get("englishIPA") or "").strip()
    e.englishIPAru = (request.form.get("englishIPAru") or "").strip()
    e.russianWord = (request.form.get("russianWord") or "").strip()
    e.russianIPA = (request.form.get("russianIPA") or "").strip()
    e.russianIPAen = (request.form.get("russianIPAen") or "").strip()
    e.level = (request.form.get("level") or "").strip()

    db.session.commit()
    flash("Запись обновлена", "success")
    return redirect(url_for("ui.edit_dictionary", dict_id=dict_id))


@bp.post("/<int:dict_id>/entry/<int:entry_db_id>/delete")
@jwt_required()
def delete_entry_ui(dict_id: int, entry_db_id: int):
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    d = Dictionary.query.get_or_404(dict_id)

    e = DictionaryEntry.query.filter_by(id=entry_db_id, dictionary_id=d.id).first_or_404()
    db.session.delete(e)
    db.session.commit()
    flash("Запись удалена", "info")
    return redirect(url_for("ui.edit_dictionary", dict_id=dict_id))


@bp.route("/<int:dict_id>/toggle_publish", methods=["POST"])
@jwt_required()
def toggle_publish(dict_id):
    """Переключает публикацию словаря: публикует или снимает с публикации."""

    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        flash("Нет прав", "danger")
        return redirect(url_for("ui.list_dictionaries"))

    d = Dictionary.query.get_or_404(dict_id)

    try:
        if d.published:
            result = delete_dictionary_file(d)
        else:
            result = write_dictionary_file(d)
    except Exception as e:
        flash(f"Ошибка при работе с файлом словаря: {e}", "danger")
        return redirect(url_for("ui.dashboard"))

    if result:
        increment_global_meta()

        d.published = not d.published
        db.session.commit()

        status = "опубликован" if d.published else "снят с публикации"
        flash(f"Словарь {d.language} {d.level} {status}", "success")
    else:
        flash("Не удалось обновить статус словаря", "danger")

    return redirect(url_for("ui.dashboard"))

