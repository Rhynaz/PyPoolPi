from flask import Blueprint, request

from utils.log import get_log_lines

LOG = Blueprint("log", __name__, url_prefix="/log")


@LOG.get("/")
def view_log():
    lines = request.args.get("lines", 0, type=int)
    response = "\n".join(get_log_lines()[-lines:])
    return response, 200, {"Content-Type": "text/plain"}
