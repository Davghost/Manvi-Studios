from flask import Blueprint, render_template, request, redirect, url_for, session
from decorators import login_required, professor_required, aluno_required
from db import get_connect

professor_bp = Blueprint("professor", __name__, template_folder="templates")

@professor_bp.route("/dashboard")
@professor_required
def dashboard():
   with get_connect() as con:
      teacher_id = session["user_id"]
      cur = con.cursor()

      data_alunos = cur.execute("""
         SELECT user_profile.user_id, user_profile.name, user_profile.serie FROM user_profile
         JOIN teacher_profile ON teacher_profile.institution = user_profile.institution
         WHERE teacher_profile.teacher_id = ?
         
         ORDER BY
          CASE user_profile.serie
             WHEN '9°Ano' THEN 1
             WHEN '1°Ano EM' THEN 2
             WHEN '2°Ano EM' THEN 3
             WHEN '3°Ano EM' THEN 4
             ELSE 99
          END,
          user_profile.name;
         """, (teacher_id,)).fetchall()
      
      ordem_series = ["9°Ano", "1°Ano EM", "2°Ano EM", "3°Ano EM"]

      grupos = {serie: [] for serie in ordem_series}

      for user_id, nome, serie in data_alunos:
         if serie in grupos:
            grupos[serie].append({"user_id": user_id, "name": nome})
      
      return render_template("prof_dash.html", grupos=grupos)

@professor_bp.route("/createExam", methods=["GET", "POST"])
@professor_required
def createExam():
   if request.method == "GET":
      return render_template("prof_exam_perso.html")
      
   title = request.form.get("nomeProva")
   description = request.form.get("descricaoProva")

   con = get_connect()
   cur = con.cursor()

   cur.execute("""
       INSERT INTO exam (title, description)
       VALUES (?, ?)
   """, (title, description))

   exam_id = cur.lastrowid

   questoes = {}
   for key in request.form:
       if key.startswith("questoes"):

           index = key.split("[")[1].split("]")[0]
           campo = key.split("[")[2].replace("]", "")
           if index not in questoes:
               questoes[index] = {}
           questoes[index][campo] = request.form[key]

   for q in questoes.values():
       cur.execute("""
           INSERT INTO question (exam_id, statement, opt_a, opt_b, opt_c, opt_d, correct_option)
           VALUES (?, ?, ?, ?, ?, ?, ?)
       """, (
           exam_id,
           q["enunciado"],
           q["A"],
           q["B"],
           q["C"],
           q["D"],
           q["correta"]
       ))

   con.commit()
   cur.close()
   con.close()
   return "Prova cadastrada com sucesso!"