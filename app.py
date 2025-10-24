from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

#from flask_httpauth import HTTPBasicAuth
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
from db import get_connect
from auth import auth_blueprint

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.register_blueprint(auth_blueprint, url_prefix="/auth")


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.auth"))
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@login_required
def main():
    username = session.get("username")
    return render_template("main.html", username=username)

@app.route("/about_us")
def about_us():
    return render_template("about_us.html")

@app.route("/oftenquestions")
def oftenquestions():
    return render_template("oftenquestions.html")

@app.route("/exam/<int:exam_id>")
@login_required
def exam(exam_id):
    con = get_connect()
    cur = con.cursor()
    exam = cur.execute("SELECT * FROM exam WHERE id = ?", (exam_id,)).fetchone()
    questions = cur.execute("SELECT * FROM question WHERE exam_id = ?", (exam_id,)).fetchall()
    cur.close()
    con.close()
    return render_template("exam.html", exam=exam, questions=questions)

@app.route("/submit_result", methods=["POST"])
@login_required
def submit_result():
    data = request.form
    respostas = {}
    exam_id = data.get("exam_id")
    qntd_acertos = 0

    for key in data.keys():
        if key.startswith("q"):
            respostas[key] = data.get(key)

    con = get_connect()
    cur = con.cursor()

    cur.execute("SELECT id, correct_option FROM question WHERE exam_id = ?", (exam_id,))
    resp_right = cur.fetchall()

    for resp in resp_right:
        resp_user = respostas.get(f"q{resp['id']}")
        if resp_user == resp["correct_option"]:
            qntd_acertos +=1
    
    cur.execute("INSERT INTO user_result (exam_id, correct, total) VALUES (?,?,?)", (exam_id, qntd_acertos, len(resp_right)))
    con.commit()
    cur.close()
    con.close()

    return redirect(url_for("main"))

if __name__ == "__main__":
    app.run(debug=True)