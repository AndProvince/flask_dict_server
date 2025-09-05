from flask import Blueprint, render_template, redirect, url_for, flash
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db
from ..models.user import User
from ..models.clients import Client

bp = Blueprint("clients_admin", __name__, url_prefix="/dictionary")


@bp.get("/clients/all")
@jwt_required()
def clients_list():
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    clients = Client.query.order_by(Client.id.asc()).all()
    total = len(clients)
    return render_template("clients_list.html", clients=clients, total=total)


@bp.post("/clients/<int:client_id>/delete")
@jwt_required()
def delete_client(client_id: int):
    user_id = int(get_jwt_identity())

    user = User.query.get(user_id)
    if not user or not user.is_admin:
        flash("Авторизуйтесь", "warning")
        return redirect(url_for("ui.login_page"))

    c = Client.query.get_or_404(client_id)
    db.session.delete(c)
    db.session.commit()
    flash(f"Клиент {c.email} удалён", "success")
    return redirect(url_for("clients_admin.clients_list"))