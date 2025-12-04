from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "gnib-school-project-key"

# adding the upload logic and determining the file type
# that is acceptable and the maximum size it should take.
# Upload Settings refrence:  file uploads pattern.  Flask Docs 
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 5

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# This dictionary is based on the project structure and was 
#generated and structured by ChatGPT with the help of the project description.

DOC_MAP = {
    "study": {
        "masters": [
            "passport",
            "college_letter",
            "fees_proof",
            "scholarship_proof",
            "course_start_proof",
            "insurance",
        ],
        "undergraduate": [
            "passport",
            "college_letter",
            "fees_proof",
            "scholarship_proof",
            "insurance",
        ],
        "english_language": [
            "passport",
            "college_letter",
            "fees_proof",
            "insurance",
        ],
    },
    "work": {
        "employment_permit": [
            "passport",
            "employment_letter",
            "payslip",
            "insurance",
        ],
        "graduate_1g": [
            "passport",
            "college_letter",
            "insurance",
        ],
    },
}

# checking if the file extension is allowed
def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_required_docs(purpose: str, category: str):
    return DOC_MAP.get(purpose, {}).get(category, [])

#created sessions to keep track of the selected purpose, category and uploaded documents

def ensure_session_store():
    session.setdefault("purpose", None)
    session.setdefault("category", None)
    session.setdefault("uploaded_docs", {})
