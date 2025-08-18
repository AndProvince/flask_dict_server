import os
from flask import Flask
from .config import Config
from .extensions import db, jwt, migrate
from .routes import auth_bp, dictionaries_bp, ui_bp, users_admin_bp
from app.models import User


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    # Ensure output dir exists
    os.makedirs(app.config["DICTIONARIES_DIR"], exist_ok=True)

    # Init extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dictionaries_bp)
    app.register_blueprint(ui_bp)
    app.register_blueprint(users_admin_bp)

    # Create DB schemas (dev convenience; for prod use migrations)
    with app.app_context():
        db.create_all()

        if User.query.count() == 0:
            admin = User(username="admin",email="admin@vp.com", is_admin=True)
            admin.set_password("Qw123456")
            db.session.add(admin)
            db.session.commit()
            print("Создан админ: admin/Qw123456")

    return app