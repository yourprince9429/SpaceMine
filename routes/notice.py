from flask import Blueprint

from handlers.notice import get_notices

notice_bp = Blueprint("notice", __name__)


@notice_bp.route("/api/notices")
def notices():
    return get_notices()
