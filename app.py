from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

#Sem uso
#from flask_httpauth import HTTPBasicAuth
from decorators import login_required, professor_required, aluno_required

from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_connect
from auth import auth_blueprint
from user_profile.routes import profile_bp
from professor.routes import professor_bp

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.register_blueprint(auth_blueprint, url_prefix="/auth")
app.register_blueprint(profile_bp, url_prefix="/user")
app.register_blueprint(professor_bp, url_prefix="/teacher")

@app.route('/')
def main():
    con = get_connect()
    cur = con.cursor()
    user_id = session.get("user_id")

    role = session.get("role")
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"

    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()

    username = session.get("username")
    cur.close()
    con.close()
    return render_template("main.html", username=username, role=session.get("role"), profile=profile)

@app.route("/about_us")
def about_us():
    con = get_connect()
    cur = con.cursor()

    user_id = session.get("user_id")

    role = session.get("role")
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"
    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()
    return render_template("about_us.html", profile=profile)

@app.route("/oftenquestions")
def oftenquestions():
    con = get_connect()
    cur = con.cursor()

    user_id = session.get("user_id")

    role = session.get("role")
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"
    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()

    return render_template("oftenquestions.html", profile=profile)

@app.route("/exam/<int:exam_id>")
@login_required
@aluno_required
def exam(exam_id):
    con = get_connect()
    cur = con.cursor()
    exam = cur.execute("SELECT * FROM exam WHERE id = ?", (exam_id,)).fetchone()
    questions = cur.execute("SELECT * FROM question WHERE exam_id = ?", (exam_id,)).fetchall()
    #answers_render = cur.execute("SELECT question_id, selected_option FROM user_answer WHERE user_id = ? AND exam_id = ?", (session['user_id'], exam_id)).fetchall()
    #answer = {ua["question_id"]: ua["selected_option"] for ua in answers_render}

    user_id = session.get("user_id")

    role = session.get("role")
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"

    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()
    cur.close()
    con.close()

    return render_template("exam.html", exam=exam, questions=questions, profile=profile)

@app.route("/exam_result/<int:exam_id>")
@login_required
@aluno_required
def exam_result(exam_id):
    user_id = session["user_id"]
    con = get_connect()
    cur = con.cursor()
    role = session.get("role")
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"

    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()
    
    questions = cur.execute("""
        SELECT * FROM question WHERE exam_id = ?
    """, (exam_id,)).fetchall()

    user_answers = cur.execute("""
        SELECT question_id, selected_option FROM user_answer WHERE exam_id = ? AND user_id = ?         
    """, (exam_id, user_id)).fetchall()

    answer_dict = {ua["question_id"]: ua["selected_option"] for ua in user_answers}

    correct_dict = {q["id"]: q["correct_option"] for q in questions}

    exam = cur.execute("SELECT * FROM exam WHERE id = ?", (exam_id,)).fetchone()

    cur.close()     
    con.close()
    return render_template("exam.html", exam=exam, questions=questions, answers=answer_dict, submit=True, correct_options=correct_dict, profile=profile)
#exam_result.html

@app.route("/submit_result", methods=["POST"])
@login_required
@aluno_required
def submit_result():
    user_id = session.get("user_id")
    data = request.form
    respostas = {}
    exam_id = data.get("exam_id")
    qntd_acertos = 0

    for key in data.keys():
        if key.startswith("q"):
            respostas[key] = data.get(key)

    con = get_connect()
    cur = con.cursor()

    role = session.get("role")
    if role == "aluno":
        table = "user_profile"
        id_column = "user_id"
    else:
        table = "teacher_profile"
        id_column = "teacher_id"

    profile = cur.execute(
        f"SELECT * FROM {table} WHERE {id_column} = ?",
        (user_id,)
    ).fetchone()

    cur.execute("SELECT id, correct_option FROM question WHERE exam_id = ?", (exam_id,))
    resp_right = cur.fetchall()

    for resp in resp_right:
        resp_user = respostas.get(f"q{resp['id']}")
        if resp_user == resp["correct_option"]:
            qntd_acertos += 1

    last_submission = cur.execute("SELECT MAX(submission_exam_id) FROM user_answer WHERE user_id = ? AND exam_id = ?", (user_id, exam_id)).fetchone()[0] or 0
    new_submission = last_submission + 1

    for key, selected_option in respostas.items():
        question_id = int(key[1:])
        cur.execute(
            "INSERT INTO user_answer(user_id, exam_id, question_id, selected_option, submission_exam_id) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], exam_id, question_id, selected_option, new_submission)
        )

    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("exam_result", exam_id=exam_id))

@app.route("/myexams")
@login_required
@aluno_required
def examToStudy():
    con = get_connect()
    cur = con.cursor()

    exams = cur.execute("SELECT * FROM exam").fetchall()

    cur.close()
    con.close()

    return render_template("exams_teste.html", exams=exams)

@app.route("/examHistory", methods=["GET", "POST"])
@login_required
@aluno_required
def examHistory():
    role = session.get("user_id")

    with get_connect() as con:
        cur = con.cursor()
        
        user_id = session["user_id"]
        role = session.get("role")
        if role == "aluno":
            table = "user_profile"
            id_column = "user_id"
        else:
            table = "teacher_profile"
            id_column = "teacher_id"

        profile = cur.execute(
            f"SELECT * FROM {table} WHERE {id_column} = ?",
            (user_id,)
        ).fetchone()

        exam_prevs = cur.execute("""                
            SELECT title, description FROM exam
        """).fetchall()

        prevs_result = cur.execute("""
            SELECT DISTINCT exam_id, submission_exam_id
            FROM user_answer
            WHERE user_id = ?
            ORDER BY submission_exam_id DESC
        """, (user_id,)).fetchall()

    return render_template("examHistory.html", exam_prevs=exam_prevs, prevs_result=prevs_result, profile=profile)


if __name__ == "__main__":
    app.run(debug=True)
