from flask import Flask, render_template
from waitress import serve

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # app.run("0.0.0.0", 8000, debug=True)
    serve(app, listen="localhost:8000")
