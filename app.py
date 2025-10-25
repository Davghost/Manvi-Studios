from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static', template_folder='templates')

def get_connect():
    con = sqlite3.connect('questions_bank.db')
    con.row_factory = sqlite3.Row
    return con

# --- ROTAS PRINCIPAIS ---

@app.route("/")
def home():
    return redirect(url_for("main"))

@app.route("/authentic")
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
    for key in data:
        respostas[key] = data[key]
    return "Resultado recebido com sucesso!"


# --- NOVAS PÁGINAS HTML ---
@app.route("/about-us")
def about_us():
    return render_template("about_us.html")

@app.route("/oftenquestions")
def oftenquestions():
    return render_template("oftenquestions.html")


# --- EXECUÇÃO ---
if __name__ == "__main__":
    app.run(debug=True)
