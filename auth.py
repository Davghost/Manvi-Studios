#from flask_httpauth import HTTPBasicAuth
from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_connect

import re

auth_blueprint = Blueprint("auth", __name__, template_folder="templates")

@auth_blueprint.route("/", methods=["GET", "POST"])
def auth():
    error = None
    if request.method == "POST":
        form_type = request.form.get("form_type")
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        con = get_connect()
        cur = con.cursor()

        if form_type == "login-aluno":
            user = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                cur.execute(
                    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                    (session["user_id"],)
                )
                con.commit()
                cur.close()
                con.close()
                return redirect(url_for("main"))
            else:
                error = "Usuário ou senha incorretos"
                


        elif form_type == "cadastro-aluno":
            x = re.search("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+(\.com(\.[A-Za-z]{2})?|\.[A-Za-z]{3,})$", email)

            if not x:
              error = "Email inválido"
            
            else:
                exists = cur.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
                if exists:
                    error = "Usuário ou email já cadastrado"
                else:
                    password_hash = generate_password_hash(password)
                    cur.execute("""
                    INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)
                    """, (username, email, password_hash))

                    con.commit()
                    session["user_id"] = cur.lastrowid
                    session["username"] = username
                    cur.close()
                    con.close()
                    return redirect(url_for("main"))
    return render_template("authentic.html", error=error)

@auth_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.auth"))
