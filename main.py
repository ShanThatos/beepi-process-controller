import os
import subprocess

from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, session
from waitress import serve

load_dotenv()

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY")

@app.before_request
def before_request():
    print(f"[{request.method} REQUEST] from {request.remote_addr}\n\t{request.url}")


@app.route("/")
def index():
    session.clear()
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("username", "") == os.environ.get("PCR_USERNAME") and request.form.get("password", "") == os.environ.get("PCR_PASSWORD"):
        session["is_admin"] = True
        return redirect("/admin")
    return redirect("/")

@app.route("/admin")
def admin():
    if not session.get("is_admin", False):
        return redirect("/")
    return "admin page"



if __name__ == "__main__":
    # cloudflared tunnel run --url 0.0.0.0:8000 beepi.shanthatos.dev
    subprocess.Popen(["cloudflared", "tunnel", "run", "--url", "0.0.0.0:8000", "beepi.shanthatos.dev"])

    # app.run("0.0.0.0", 8000, debug=True)
    serve(app, listen="0.0.0.0:8000", threads=1)
