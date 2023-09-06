import atexit
import psutil
import json
from collections import deque
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from threading import Thread
from typing import Deque, List, Literal, Optional, TypedDict, NotRequired

import extensions as ext
import utils

projects_dir = Path(str(ext.PROJECTS_DIR)).resolve()
projects_file = projects_dir.joinpath("_projects.json")
projects: List["ActiveProject"] = []


class ProjectData(TypedDict):
    name: str
    folder_name: str
    update_command: str
    start_command: str
    autostart: bool
    capture_limit: NotRequired[int]


class ActiveProject:
    def __init__(self, data: ProjectData):
        self.data = data
        self.process: Optional[Popen] = None
        self.capture: Optional[PopenCapture] = None
        self.update_process: Optional[Popen] = None
        self.update_capture: Optional[PopenCapture] = None

        atexit.register(self.stop_if_exists)

        if data["autostart"]:
            self.start()

    def get_working_dir(self) -> Path:
        global projects_dir
        return projects_dir.joinpath(self.data["folder_name"])

    def stop_if_exists(self):
        for process_attr in ("process", "update_process"):
            process: Optional[Popen] = getattr(self, process_attr)
            if process is None: continue
            if not psutil.pid_exists(process.pid): continue
            for child_process in psutil.Process(process.pid).children(True):
                child_process.kill()
            process.kill()
            setattr(self, process_attr, None)

    def start(self):
        self.stop_if_exists()
        self.process = Popen(self.data["start_command"], cwd=self.get_working_dir(), bufsize=1, stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        self.capture = PopenCapture(self.process, self.data.get("capture_limit"))

    def update(self):
        self.stop_if_exists()
        self.update_process = Popen(self.data["update_command"], cwd=self.get_working_dir(), bufsize=1, stdin=PIPE, stdout=PIPE, stderr=STDOUT, universal_newlines=True)
        self.update_capture = PopenCapture(self.update_process)

    def get_status(self) -> Literal["running", "stopped", "updating"]:
        if self.update_process is not None and self.update_process.poll() is None:
            return "updating"
        if self.process is not None and self.process.poll() is None:
            return "running"
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


def get_project(project_name: str):
    return next(p for p in get_projects() if p.data["name"] == project_name)
