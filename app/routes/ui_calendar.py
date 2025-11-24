from flask import Blueprint, send_file, request, url_for
import random
from datetime import datetime
from ..clndr2026 import generate_calendar, createLines, create_calendar_image

bp = Blueprint("ui_calendar", __name__, url_prefix="/calendar")

@bp.get("/")
def home():
    calendar_link = url_for('ui_calendar.calendar_2026', _external=True)
    return f"""
    <h1>🗓 Useless Calendar 2026</h1>
    <p>Get your calendar as PNG:</p>
    <a href="{calendar_link}">{calendar_link}</a>
    """

@bp.route("/2026")
def calendar_2026():
    year = int(request.args.get("year", datetime.now().year + 1))
    hide = random.random()
    clndr = generate_calendar(year, hide_probability=hide)
    lines = createLines(clndr, year, hide)
    print(lines)
    img_buf = create_calendar_image(lines, 3840, 2160)
    return send_file(img_buf, mimetype="image/png")