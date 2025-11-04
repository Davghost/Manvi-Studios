from flask import session, redirect, url_for
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.auth"))
        return f(*args, **kwargs)
    return decorated