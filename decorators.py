from flask import session, redirect, url_for
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.auth"))
        return f(*args, **kwargs)
    return decorated

def professor_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "professor":
            return redirect(url_for("main"))
        return f(*args, **kwargs)
    return decorated

def aluno_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("role") != "aluno":
            return redirect(url_for("main"))
        return f(*args, **kwargs)
    return decorated

def logout_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get("user_id"):
            return redirect(url_for("main"))  # já logado, não volta para login
        return f(*args, **kwargs)
    return wrapper