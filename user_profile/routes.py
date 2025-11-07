from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connect
from decorators import login_required
from .utils import save_profile_picture
profile_bp = Blueprint("profile", __name__, template_folder="templates")

@profile_bp.route("/profile", methods=["GET", "POST"])
@login_required
def view_profile():
    role = session.get("role")

    if role not in ("aluno", "professor"):
        return redirect(url_for("auth.auth"))
    
    user_id = session.get("user_id")
    con = get_connect()
    cur = con.cursor()

    # === Escolher tabela certa ===
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"

    # === Buscar perfil existente ===
    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()

    if request.method == "POST":

        # Campos básicos
        name = request.form.get("name")
        institution = request.form.get("institution")
        birth_date = request.form.get("birth_date")
        bio = request.form.get("bio")
        country = request.form.get("country")
        city = request.form.get("city")
        state = request.form.get("state")

        profile_picture_file = request.files.get("profile_picture")
        profile_picture_path = None

        if profile_picture_file:
            profile_picture_path = save_profile_picture(profile_picture_file, user_id)

        # === Se já existe perfil → UPDATE ===
        if profile:
            # Preencher campos não enviados
            name = name or profile["name"]
            institution = institution or profile["institution"]
            birth_date = birth_date or profile["birth_date"]
            bio = bio or profile["bio"]
            country = country or profile["country"]
            city = city or profile["city"]
            state = state or profile["state"]

            if profile_picture_path:
                cur.execute(f"""
                    UPDATE {table}
                    SET name=?, institution=?, birth_date=?, bio=?, country=?,
                        city=?, state=?, profile_picture=?
                    WHERE {id_column}=?
                """, (name, institution, birth_date, bio, country, city, state, profile_picture_path, user_id))
            else:
                cur.execute(f"""
                    UPDATE {table}
                    SET name=?, institution=?, birth_date=?, bio=?, country=?,
                        city=?, state=?
                    WHERE {id_column}=?
                """, (name, institution, birth_date, bio, country, city, state, user_id))

        # === Se não existe perfil → INSERT ===
        else:
            if profile_picture_path:
                cur.execute(f"""
                    INSERT INTO {table}
                    ({id_column}, name, institution, birth_date, bio, country, city, state, profile_picture)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, name, institution, birth_date, bio, country, city, state, profile_picture_path))
            else:
                cur.execute(f"""
                    INSERT INTO {table}
                    ({id_column}, name, institution, birth_date, bio, country, city, state)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_id, name, institution, birth_date, bio, country, city, state))

        con.commit()
        cur.close()
        con.close()

        return redirect(url_for("profile.view_profile"))

    cur.close()
    con.close()
    
    return render_template("user_profile.html", profile=profile)
