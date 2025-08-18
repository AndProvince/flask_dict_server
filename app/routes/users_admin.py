from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User

bp = Blueprint("users_admin", __name__)

def _current_admin():
    """Возвращает (user_id:int, user:User|None). Флешит и редиректит пусть вызывающие роуты сами."""
    try:
        uid = int(get_jwt_identity())
    except Exception:
        uid = 0
    user = User.query.get(uid) if uid else None
    return uid, user

def _require_admin():
    """Возвращает (User) или None и редиректит через вызвавший код."""
    _, user = _current_admin()
    if not user or not user.is_admin:
        return None
    return user

@bp.get("/users")
@jwt_required()
def list_users():
    admin = _require_admin()
    if not admin:
        flash("Доступ только для администраторов", "danger")
        return redirect(url_for("ui.index"))

    users = User.query.order_by(User.id.asc()).all()
    admins_count = User.query.filter_by(is_admin=True).count()
    return render_template("users_list.html", users=users, admins_count=admins_count, me_id=admin.id)


@bp.post("/create")
@jwt_required()
def create_user():
    admin = _require_admin()
    if not admin:
        flash("Доступ только для администраторов", "danger")
        return redirect(url_for("ui.index"))

    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    is_admin = request.form.get("is_admin").lower() in ("true", "1", "yes", "on")

    if not username or not password:
        flash("Все поля обязательны")
        return redirect(url_for("users_admin.list_users"))

    if password != password2:
        flash("Пароли не совпадают")
        return redirect(url_for("users_admin.list_users"))

    if User.query.filter_by(username=username).first():
        flash("Такой пользователь уже существует")
        return redirect(url_for("users_admin.list_users"))

    new_user = User(
        username=username,
        email=email,
        is_admin=is_admin,
    )
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    flash(f"Пользователь {username} создан", "success")
    return redirect(url_for("users_admin.list_users"))


@bp.post("/users/<int:user_id>/password")
@jwt_required()
def change_password(user_id: int):
    admin = _require_admin()
    if not admin:
        flash("Доступ только для администраторов", "danger")
        return redirect(url_for("ui.index"))

    user = User.query.get_or_404(user_id)

    new_password = (request.form.get("new_password") or "").strip()
    new_password2 = (request.form.get("new_password2") or "").strip()

    if not new_password or len(new_password) < 6:
        flash("Пароль должен быть не короче 6 символов", "warning")
        return redirect(url_for("users_admin.list_users"))

    if new_password != new_password2:
        flash("Пароли не совпадают", "warning")
        return redirect(url_for("users_admin.list_users"))

    user.set_password(new_password)
    db.session.commit()
    flash(f"Пароль пользователя {user.username} обновлён", "success")
    return redirect(url_for("users_admin.list_users"))

@bp.post("/users/<int:user_id>/delete")
@jwt_required()
def delete_user(user_id: int):
    admin = _require_admin()
    if not admin:
        flash("Доступ только для администраторов", "danger")
        return redirect(url_for("ui.index"))

    if admin.id == user_id:
        flash("Нельзя удалить свою учётную запись", "warning")
        return redirect(url_for("users_admin.list_users"))

    user = User.query.get_or_404(user_id)

    # запрещаем удалять последнего админа
    if user.is_admin:
        admins_count = User.query.filter_by(is_admin=True).count()
        if admins_count <= 1:
            flash("Нельзя удалить последнего администратора", "danger")
            return redirect(url_for("users_admin.list_users"))

    db.session.delete(user)
    db.session.commit()
    flash(f"Пользователь {user.username} удалён", "success")
    return redirect(url_for("users_admin.list_users"))
