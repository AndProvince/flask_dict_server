import os
import uuid
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app, send_from_directory, flash
from ..models.projects import Project
from werkzeug.utils import secure_filename
from app.extensions import db
from datetime import datetime
from collections import defaultdict
from itertools import groupby

bp = Blueprint("ui_main", __name__, url_prefix="")

# --- UI pages ---

@bp.context_processor
def inject_year():
    return {'current_year': datetime.utcnow().year}

@bp.route("/")
def index():
    projects = Project.query.filter_by(type="project") \
        .order_by(Project.created_at.desc()).all()
    events = Project.query.order_by(Project.date.desc()).all()

    # группируем по году
    events_grouped = defaultdict(list)
    for year, items in groupby(events, key=lambda e: e.date.year):
        events_grouped[year] = list(items)

    return render_template("main.html", projects=projects, events_grouped=events_grouped)



@bp.route("/events")
def events():
    page = int(request.args.get("page", 1))
    per_page = 5
    pagination = Project.query.filter_by(type="event")\
        .order_by(Project.date.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for e in pagination.items:
        tags_list = [t.strip() for t in e.tags.split(",")] if e.tags else []
        items.append({
            "id": e.id,
            "title": e.title,
            "date": e.date.strftime("%Y-%m-%d"),
            "summary": e.summary,
            "desc": e.summary,  # оставим для старого фронта
            "image_url": e.image_url,
            "link": e.link,
            "tags": tags_list,  # <-- теперь список!
        })

    return jsonify({
        "items": items,
        "has_more": pagination.has_next
    })


@bp.route("/admin", methods=["GET", "POST"])
def admin():
    edit_id = request.args.get("edit")
    project = None
    if edit_id:
        project = Project.query.get(edit_id)

    if request.method == "POST":
        pid = request.form.get("id")  # скрытое поле для редактирования
        if pid:
            project = Project.query.get_or_404(pid)
        else:
            project = Project(created_at=datetime.utcnow())
            db.session.add(project)

        project.type = request.form.get("type")
        project.title = request.form.get("title")
        project.summary = request.form.get("summary")
        project.tags = request.form.get("tags")
        project.link = request.form.get("link")
        project.date = datetime.strptime(request.form.get("date"), "%Y-%m-%d")

        image_file = request.files.get("image")
        if image_file and image_file.filename:
            # удалить старый файл, если был
            if project.image_url:
                old_path = os.path.join(current_app.config["UPLOAD_DIR"], project.image_url)
                if os.path.exists(old_path):
                    os.remove(old_path)

            filename = secure_filename(image_file.filename)
            upload_dir = current_app.config["UPLOAD_DIR"]
            os.makedirs(upload_dir, exist_ok=True)
            save_path = os.path.join(upload_dir, filename)
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(save_path):
                filename = f"{base}_{counter}{ext}"
                save_path = os.path.join(upload_dir, filename)
                counter += 1

            image_file.save(save_path)
            project.image_url = filename

        db.session.commit()
        flash("Item saved!", "success")
        return redirect(url_for("ui_main.admin"))

    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template("padmin.html", projects=projects, project=project)


@bp.route("/admin/delete/<int:pid>", methods=["POST"])
def delete_project(pid):
    project = Project.query.get_or_404(pid)

    # удалить файл картинки
    if project.image_url:
        file_path = os.path.join(current_app.config["UPLOAD_DIR"], project.image_url)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(project)
    db.session.commit()
    flash("Item deleted!", "info")
    return redirect(url_for("ui_main.admin"))


@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(current_app.config['UPLOAD_DIR'], filename)


@bp.route("/uploads/download/<path:filename>")
def download_file(filename):
    return send_from_directory(
        current_app.config["UPLOAD_DIR"],
        filename,
        as_attachment=True
    )
