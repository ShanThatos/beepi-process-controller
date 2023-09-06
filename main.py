import os
from functools import cache, wraps
from subprocess import CREATE_NEW_PROCESS_GROUP, DETACHED_PROCESS, Popen
from typing import Callable

from flask import Flask, abort, redirect, render_template, request, session
from waitress import serve

import extensions as ext
import manage

app = Flask(__name__)
app.secret_key = ext.SECRET_KEY
app.config["TEMPLATES_AUTO_RELOAD"] = True


@cache
def get_macro(template_path: str, macro_name: str) -> Callable[..., str]:
    return getattr(app.jinja_env.get_template(template_path).module, macro_name)
def render_macro(macro_path: str, *args, **kwargs) -> str:
    return get_macro(*macro_path.split(":"))(*args, **kwargs)


def auth_admin(f: Callable):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin", False):
            abort(418)
        return f(*args, **kwargs)
    return wrapper


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        if not session.get("is_admin", False):
            return render_template("login.html")
        else:
            return render_template("index.html", projects=manage.get_projects())
    if request.form.get("username", "") == ext.PCR_USERNAME and request.form.get("password", "") == ext.PCR_PASSWORD:
        session["is_admin"] = True
    return redirect("/")


@app.route("/logout", methods=["GET"])
def logout():
    session["is_admin"] = False
    return redirect("/")


@app.route("/<string:project_name>/<string:action>", methods=["GET", "POST"])
@auth_admin
def project_action(project_name: str, action: str):
    project = manage.get_project(project_name)
    if request.method == "GET":
        if action == "output":
            return project.get_output()
        elif action == "update_output":
            return project.get_update_output()
        elif action == "status":
            return render_macro("project.html:project_status", project)
        elif action == "buttons":
            return render_macro("project.html:project_buttons", project)
    elif request.method == "POST":
        if action == "start":
            project.start()
        elif action == "stop":
            project.stop_if_exists()
        elif action == "update":
            project.update()
        return render_macro("project.html:project_row", project)


@app.route("/restart", methods=["POST"])
@auth_admin
def restart():
    for project in manage.get_projects():
        project.stop_if_exists()
    Popen("make restart", shell=True, creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
    os._exit(0)


def start_server():
    # cloudflared tunnel run --url 0.0.0.0:8000 beepi.shanthatos.dev
    Popen(["cloudflared", "tunnel", "run", "--url", "0.0.0.0:8000", "beepi.shanthatos.dev"])
    
    # app.run("0.0.0.0", 8000, debug=False, load_dotenv=False, use_reloader=False)
    serve(app, listen="0.0.0.0:8000")

if __name__ == "__main__":
    start_server()
