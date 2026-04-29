import os
import json

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/uploads")
assert UPLOAD_DIR

REPORTS_DIR = "/reports"
ALLOWED_DIR = os.environ.get("ALLOWED_DIR", "/sessions")

def read_invoice(filename):
    filename = os.path.basename(filename)
    path = os.path.join(UPLOAD_DIR, filename)
    assert path.startswith(UPLOAD_DIR)
    try:
        with open(path, "r") as f:
            return f.read()
    except OSError:
        return None

def load_session(session_file):
    session_file = os.path.realpath(session_file)
    assert session_file.startswith(ALLOWED_DIR)
    with open(session_file, "r") as f:
        return json.load(f)

def save_report(name, content):
    name = os.path.basename(name)
    path = os.path.join(REPORTS_DIR, f"{name}.txt")
    with open(path, "w") as f:
        f.write(content)

def list_files(directory):
    try:
        return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except OSError:
        return []

def delete_temp(filename):
    filename = os.path.basename(filename)
    path = os.path.join("/tmp", filename)
    if os.path.exists(path) and os.path.isfile(path):
        try:
            os.remove(path)
        except OSError:
            pass

def get_file_size(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None