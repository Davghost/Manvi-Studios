from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv
import os
import sqlite3

app = Flask(__name__)

def get_connect():
    con = sqlite3.connect("questions_bank.db")
    con.row_factory = sqlite3.Row
    return con

@app.route("/")
def authentic():
    return render_template("authentic.html")

@app.route("/main-page")
def main():
    return render_template("main.html")

@app.route("/exam/<int:exam_id>")
def exam(exam_id):
    con = get_connect()
    cur = con.cursor()
    exam = cur.execute("SELECT * FROM exam WHERE id = ?", (exam_id,)).fetchone()
    questions = cur.execute("SELECT * FROM question WHERE exam_id = ?", (exam_id,)).fetchall()
    cur.close()
    con.close()
    return render_template("exam.html", exam=exam, questions=questions)

@app.route("/submit_result", methods=["POST"])
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