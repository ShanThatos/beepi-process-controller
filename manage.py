import atexit
import json
import os
from collections import deque
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from threading import Thread
import threading
from typing import Deque, Dict, List, Literal, NotRequired, Optional, Tuple, TypedDict

import psutil
from git.util import rmtree as gitrmtree
from pydantic import TypeAdapter, ValidationError

import extensions as ext
import utils

projects_dir = Path(str(ext.PROJECTS_DIR)).resolve()
projects_file = projects_dir.joinpath("_projects.json")
projects: List["ActiveProject"] = []

def fully_kill_process(process: Optional[Popen]):
    if process is None: return
    for child_process in psutil.Process(process.pid).children(True):
        child_process.kill()
    process.kill()


class ProjectData(TypedDict):
    name: str
    short_name: str
    update_command: str
    start_command: str
    autostart: bool
    git: NotRequired[str]
    capture_limit: NotRequired[int]
    environment: NotRequired[Dict[str, str]]

PROJECT_DATA_VALIDATOR = TypeAdapter(ProjectData)

class ActiveProject:
    def __init__(self, data: ProjectData):
        self.data = data
        self.lock = threading.Lock()
        self.process: Optional[Popen] = None
        self.capture: Optional[PopenCapture] = None
        self.update_process: Optional[Popen] = None
        self.update_capture: Optional[PopenCapture] = None

        atexit.register(self.stop_if_exists)

        if data.get("autostart") and self.is_valid():
            self.start()

    def is_valid(self) -> bool:
        try:
            PROJECT_DATA_VALIDATOR.validate_python(self.data)
            return True
        except ValidationError:
            return False

    def get_working_dir(self) -> Path:
        global projects_dir
        return projects_dir.joinpath(self.data["short_name"])

    def stop_if_exists(self):
        for process_attr in ("process", "update_process"):
            process: Optional[Popen] = getattr(self, process_attr)
            if process is None: continue
            if not psutil.pid_exists(process.pid): continue
            fully_kill_process(process)
            setattr(self, process_attr, None)

    def start(self):
        self.stop_if_exists()
        self.process, self.capture = self.__start_popen(self.data["start_command"], self.get_working_dir())

    def update(self):
        self.stop_if_exists()
        command = self.data["update_command"]
        cwd = self.get_working_dir()
        if not cwd.exists():
            if "git" not in self.data:
                print("Cannot update project without git url")
                return
            command = f"git clone {self.data["git"]} {self.data["short_name"]}"
            cwd = projects_dir
        self.update_process, self.update_capture = self.__start_popen(command, cwd)

    def __start_popen(self, command: str, cwd: Path) -> Tuple[Popen, "PopenCapture"]:
        process = Popen(command, cwd=cwd, bufsize=1, stdin=PIPE, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True, env=os.environ | self.data.get("environment", {}))
        capture = PopenCapture(process, self.data.get("capture_limit"))
        return process, capture

    def delete(self):
        self.stop_if_exists()
        if (dir := self.get_working_dir()).exists():
            gitrmtree(dir)
    
    def as_json(self) -> str:
        return json.dumps(self.data, indent=4)

    def get_status(self) -> Literal["invalid", "missing", "running", "stopped", "updating"]:
        if self.update_process is not None and self.update_process.poll() is None:
            return "updating"
        if self.process is not None and self.process.poll() is None:
            return "running"
        if not self.is_valid():
            return "invalid"
        if not self.get_working_dir().exists():
            if self.data.get("git"):
                return "missing"
            return "invalid"
        return "stopped"

    def get_output(self) -> str:
        if self.capture is None:
            return ""
        return self.capture.get_output()
    
    def get_update_output(self) -> str:
        if self.update_capture is None:
            return ""
        return self.update_capture.get_output()


class PopenCapture:
    DEFAULT_LIMIT = 100
    def __init__(self, process: Popen, limit: Optional[int] = None):
        self.process = process
        self.limit = limit or self.DEFAULT_LIMIT
        self.output: Deque[str] = deque()
        self.running = True
        Thread(target=self.capture_output, daemon=True).start()
    
    def capture_output(self):
        process_out = utils.assert_not_none(self.process.stdout)
        for line in process_out:
            if not self.running:
                break
            # print(line, end="")
            self.output.append(line)
            while self.limit and len(self.output) > self.limit:
                self.output.popleft()
    
    def get_output(self) -> str:
        return "".join(self.output).strip()
    
    def kill(self):
        self.running = False
        self.process.kill()


@utils.run_on_start
def setup():
    global projects, projects_dir, projects_file
    projects_dir.mkdir(parents=True, exist_ok=True)

    if not projects_file.exists():
        projects_file.touch()
        projects_file.write_text(r"[]")

    projects_data: List[ProjectData] = json.loads(projects_file.read_text())
    projects = [ActiveProject(d) for d in projects_data]


def get_projects() -> List[ActiveProject]:
    return projects


def save_projects():
    projects_file.write_text(json.dumps([p.data for p in projects], indent=4))


def get_project(short_name: str):
    return next((p for p in get_projects() if p.data["short_name"] == short_name), None)


def add_project(short_name: str) -> ActiveProject:
    project_data = {"short_name": short_name}
    project = ActiveProject(project_data) # type: ignore
    projects.append(project)
    save_projects()
    return project

def remove_project(project: ActiveProject):
    project.delete()
    projects.remove(project)
    save_projects()
