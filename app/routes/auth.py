from flask import Blueprint, render_template, request, redirect, make_response, session
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from ..models.user import User
from ..extensions import db

bp = Blueprint("auth", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            # создаём токен
            access_token = create_access_token(identity=str(user.id))
            resp = make_response(redirect("/"))

            # сохраняем токен в cookies
            set_access_cookies(resp, access_token)

            # сохраняем логин в session для шаблонов
            session["username"] = user.username
            session["is_admin"] = bool(user.is_admin)

            return resp

        return render_template("login.html", error="Неверный логин или пароль")

    return render_template("login.html")


@bp.route("/logout")
def logout():
    resp = make_response(redirect("/login"))

    # удаляем jwt cookies
    unset_jwt_cookies(resp)

    # убираем имя пользователя из session
    session.pop("username", None)
    session.pop("is_admin", None)

    return resp
