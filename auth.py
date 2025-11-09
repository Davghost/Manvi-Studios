#from flask_httpauth import HTTPBasicAuth
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_connect
from decorators import login_required, logout_required

import re

auth_blueprint = Blueprint("auth", __name__, template_folder="templates")

@auth_blueprint.route("/", methods=["GET", "POST"])
@logout_required
def auth():
    error = None
    if request.method == "POST":
        form_type = request.form.get("form_type")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        with get_connect() as con:
            cur = con.cursor()
            if form_type == "login-aluno":
                user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                if user and check_password_hash(user["password_hash"], password):
                    session["user_id"] = user["id"]
                    session["username"] = user["username"]
                    session["role"] = "aluno"
                    cur.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (session["user_id"],)
                    )

                    return redirect(url_for("main"))
                else:
                    error = "Usuário ou senha incorretos"

            elif form_type == "cadastro-aluno":
                x = re.search("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+(\.com(\.[A-Za-z]{2})?|\.[A-Za-z]{3,})$", email)

                if not x:
                  error = "Email inválido"

                else:
                    exists = cur.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, email,)).fetchone()
                    if exists:
                        error = "Usuário ou email já cadastrado"
                    else:
                        password_hash = generate_password_hash(password)
                        cur.execute("""
                        INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)
                        """, (username, email, password_hash))

                        session["user_id"] = cur.lastrowid
                        session["username"] = username
                        session["role"] = "aluno"


                        return redirect(url_for("main"))

            elif form_type == "cadastro-professor":
                x = re.search("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+(\.com(\.[A-Za-z]{2})?|\.[A-Za-z]{3,})$", email)

                if not x:
                    error = "Email inválido"

                else:
                    exists = cur.execute("SELECT * FROM teachers WHERE username = ? OR email = ?", (username, email,)).fetchone()
                    if exists:
                        error = "Usuário ou email já cadastrado"

                    else:
                        password_hash = generate_password_hash(password)
                        cur.execute("""
                        INSERT INTO teachers (username, email, password_hash) VALUES (?, ?, ?)
                        """, (username, email, password_hash))
                        session["user_id"] = cur.lastrowid
                        session["username"] = username
                        session["role"] = "professor"

                        return redirect(url_for("main"))

            elif form_type == "login-professor":
                teacher = cur.execute("SELECT * FROM teachers WHERE username = ?", (username,)).fetchone()
                if teacher and check_password_hash(teacher["password_hash"], password):
                    session["user_id"] = teacher["id"]
                    session["username"] = teacher["username"]
                    session["role"] = "professor"
                    cur.execute(
                        "UPDATE teachers SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                        (session["user_id"],)
                    )
                    return redirect(url_for("main"))
                else:
                    error = "Usuário ou senha incorretos"


    return render_template("authentic.html", error=error)

@auth_blueprint.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("main"))
