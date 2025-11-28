from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from db import get_connect
from decorators import login_required
from .utils import save_profile_picture
from auth import auth

profile_bp = Blueprint("profile", __name__, template_folder="templates")

@profile_bp.route("/profile/<role>/<int:user_id>")
@login_required
def show_profile(role, user_id):
    if role not in ("aluno", "professor"):
        return redirect(url_for("auth.auth"))
    
    con = get_connect()
    cur = con.cursor()

    table = "user_profile" if role == "aluno" else "teacher_profile"
    id_column = "user_id" if role == "aluno" else "teacher_id"
    
    profile = cur.execute(f"""
    SELECT * FROM {table} WHERE {id_column} = ?
    """, (user_id,)).fetchone()

    name_sch = None
    if profile and profile["institution"]:
        name_sch = cur.execute("SELECT * FROM escolas WHERE codigo_inep = ?", (profile["institution"],)).fetchone()    

    cur.close()
    con.close()

    #editable = (session.get("user_id") == user_id)

    return render_template("user_profile.html", profile=profile, name_sch=name_sch, editable=False)

@profile_bp.route("/my_profile", methods=["GET", "POST"])
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

        serie = None
        if role == "aluno":
            serie = request.form.get("series")
        # === Se já existe perfil → UPDATE ===
        if profile:
            if role == "aluno":
                serie = serie or profile["serie"]
            # Preencher campos não enviados
            name = name or profile["name"]
            institution = institution or profile["institution"]
            birth_date = birth_date or profile["birth_date"]
            bio = bio or profile["bio"]
            country = country or profile["country"]
            city = city or profile["city"]
            state = state or profile["state"]

            if profile_picture_path:
                if role == "aluno":
                    cur.execute(f"""
                        UPDATE {table}
                        SET name=?, institution=?, birth_date=?, bio=?, country=?,
                            city=?, state=?, serie=?, profile_picture=?
                        WHERE {id_column}=?
                    """, (name, institution, birth_date, bio, country, city, state, serie, profile_picture_path, user_id))
                else:
                    cur.execute(f"""
                    UPDATE {table}
                    SET name=?, institution=?, birth_date=?, bio=?, country=?,
                        city=?, state=?, profile_picture=?
                    WHERE {id_column}=?
                """, (name, institution, birth_date, bio, country, city, state, profile_picture_path, user_id)) 
                           
            else:
                if role == "aluno":
                    cur.execute(f"""
                        UPDATE {table}
                        SET name=?, institution=?, birth_date=?, bio=?, country=?,
                            city=?, state=?, serie=?
                        WHERE {id_column}=?
                    """, (name, institution, birth_date, bio, country, city, state, serie, user_id))
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
                if role == "aluno":
                    cur.execute(f"""
                        INSERT INTO {table}
                        ({id_column}, name, institution, birth_date, bio, country, city, state, serie, profile_picture)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, name, institution, birth_date, bio, country, city, state, serie, profile_picture_path))
                else:
                    cur.execute(f"""
                        INSERT INTO {table}
                        ({id_column}, name, institution, birth_date, bio, country, city, state, profile_picture)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, name, institution, birth_date, bio, country, city, state, profile_picture_path))
            else:
                if role == "aluno":
                    cur.execute(f"""
                        INSERT INTO {table}
                        ({id_column}, name, institution, birth_date, bio, country, city, state, serie)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (user_id, name, institution, birth_date, bio, country, city, state, serie))
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

    name_sch = None
    if profile and profile["institution"]:
        name_sch = cur.execute("SELECT * FROM escolas WHERE codigo_inep = ?", (profile["institution"],)).fetchone()

    cur.close()
    con.close()
    
    return render_template("user_profile.html", profile=profile, name_sch=name_sch, editable=True)
