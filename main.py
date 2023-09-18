import atexit
import json
import os
import subprocess
from functools import cache, wraps
from pathlib import Path
from subprocess import Popen
from typing import Callable, Dict, Optional

from flask import (Flask, Response, abort, make_response, redirect,
                   render_template, request, session)
from pydantic import ValidationError
from waitress import serve

import extensions as ext
import manage

app = Flask(__name__)
app.secret_key = ext.SECRET_KEY
app.config["TEMPLATES_AUTO_RELOAD"] = ext.TEMPLATES_AUTO_RELOAD

def get_macro(template_path: str, macro_name: str) -> Callable[..., str]:
    return getattr(app.jinja_env.get_template(template_path).module, macro_name)
if not ext.TEMPLATES_AUTO_RELOAD:
    get_macro = cache(get_macro)
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
    if project is None:
        abort(418)
    with project.lock:
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
            elif action == "delete":
                project.delete()
            elif action == "remove":
                manage.remove_project(project)
                return ""
            elif action == "edit":
                return render_macro("project.html:project_edit", project)
            elif action == "save":
                return handle_project_save(project, json.loads(request.form.get("project-edit", "{}")))
            return render_macro("project.html:project_row", project)

def handle_project_save(project: manage.ActiveProject, form_data: Dict) -> str | Response:
    try:
        project_data: manage.ProjectData = manage.PROJECT_DATA_VALIDATOR.validate_python(form_data)
    except ValidationError as e:
        print(e)
        return "Invalid project spec"
    if project.get_status() not in ("invalid", "missing", "stopped"):
        return "Cannot edit project while it is running or updating"
    found_project = manage.get_project(project_data["short_name"])
    if found_project and found_project != project:
        return "Project with that short_name already exists"
    
    project.data = manage.ProjectData(project_data)
    manage.save_projects()
    response = make_response()
    response.headers["HX-Refresh"] = "true"
    return response


@app.route("/add", methods=["POST"])
@auth_admin
def add_project():
    short_name = request.form.get("short_name", "")
    if not short_name or " " in short_name or manage.get_project(short_name) is not None:
        abort(418)
    project = manage.add_project(short_name)
    return render_macro("project.html:project_row", project)


@app.route("/restart", methods=["POST"])
@auth_admin
def restart():
    for project in manage.get_projects():
        project.stop_if_exists()
    manage.fully_kill_process(CF_PROCESS)
    Popen(ext.RESTART_CMD, shell=True, start_new_session=True)
    os._exit(0)

CF_PROCESS: Optional[Popen] = None

def start_server():
    global CF_PROCESS
    if ext.RUN_CLOUDFLARED:
        cf_domain = ext.CLOUDFLARED_DOMAIN
        if not Path("./cf_creds.json").exists():
            print("Retrieving cloudflare credentials...")
            subprocess.run(f"cloudflared tunnel token --cred-file cf_creds.json {cf_domain}", shell=True)
        CF_PROCESS = Popen(f"cloudflared tunnel run --cred-file cf_creds.json --url 0.0.0.0:8000 {cf_domain}", shell=True, start_new_session=True)
    atexit.register(lambda: manage.fully_kill_process(CF_PROCESS))
    
    # app.run("0.0.0.0", 8000, debug=False, load_dotenv=False, use_reloader=False)
    serve(app, listen="0.0.0.0:8000")

if __name__ == "__main__":
    start_server()
