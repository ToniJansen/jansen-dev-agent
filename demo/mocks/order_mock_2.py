import os
import pickle

UPLOAD_DIR = "/var/www/uploads"

def read_invoice(filename):
    path = UPLOAD_DIR + "/" + filename          # CRITICAL: path traversal (../../etc/passwd)
    with open(path, "r") as f:
        return f.read()

def load_session(session_file):
    with open(session_file, "rb") as f:
        return pickle.load(f)                   # CRITICAL: arbitrary code exec via pickle

def save_report(name, content):
    path = f"/reports/{name}.txt"
    os.system(f"echo '{content}' > {path}")     # CRITICAL: command injection

def list_files(directory):
    return os.listdir(directory)                # WARNING: no path sanitization

def delete_temp(filename):
    os.remove(f"/tmp/{filename}")               # WARNING: no existence check, no sanitization

def get_file_size(path):
    return os.path.getsize(path)                # INFO: no exception handling if file missing
