from .auth import bp as auth_bp
from .dictionaries import bp as dictionaries_bp
from .ui import bp as ui_bp
from .users_admin import bp as users_admin_bp

__all__ = ["auth_bp", "dictionaries_bp", "ui_bp", "users_admin_bp"]