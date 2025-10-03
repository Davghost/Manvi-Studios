from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def main():
    return render_template("main.html")

@app.route("/teacharea")
def teacharea():
    return render_template("teacharea.html")


if __name__ == "__main__":
    app.run(debug=True)