from flask import Flask, render_template, request
from dotenv import load_dotenv
import os


app = Flask(__name__)

@app.route("/")
def authentic():
    return render_template("authentic.html")

@app.route("/main-page")
def main():
    return render_template("main.html")


if __name__ == "__main__":
    app.run(debug=True)