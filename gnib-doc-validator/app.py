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

#Remodified the rout to fit my project

@app.route("/")
def index():
    ensure_session_store()
    return render_template("index.html")

#routing the upload document , using template

@app.route("/upload", methods=["GET", "POST"])
def upload():
    ensure_session_store()

    if request.method == "POST":
        purpose = request.form.get("purpose")
        category = request.form.get("category")
        doc_type = request.form.get("doc_type")
        expiry_date = request.form.get("expiry_date")  # may be empty for some docs
        file = request.files.get("document")

        errors = []

       # Validating purpose & category 
        
        if not purpose or purpose not in DOC_MAP:
            errors.append("Please select a valid purpose (study or work).")
        if not category or category not in DOC_MAP.get(purpose, {}):
            errors.append("Please select a valid category for that purpose.")

        required_docs = get_required_docs(purpose, category)

 #  Validating  document type
        if not doc_type:
            errors.append("Please select a document type.")
        elif required_docs and doc_type not in required_docs:
            errors.append("Selected document is not required for this category.")
   

   # Validating  file presence & extension
        if not file or file.filename == "":
            errors.append("Please upload a file.")
        elif not allowed_file(file.filename):
            errors.append("Only PDF, JPG, JPEG, PNG files are allowed.")

 #  Validating file size 
        
        if file and file.filename:
            file.seek(0, os.SEEK_END)
            size_bytes = file.tell()
            file.seek(0)
            if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
                errors.append(f"File must be under {MAX_FILE_SIZE_MB} MB.")


# Validate expiry date for passport
        
        if doc_type in ["passport"]:
            if not expiry_date:
                errors.append("Expiry date is required for Passport.")
            else:
                try:
                    exp = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                    if exp <= datetime.today().date():
                        errors.append("Passport appears to be expired.")
                except ValueError:
                    errors.append("Invalid expiry date format (use YYYY-MM-DD).")

# if there is an error, shos the error message and redirect.

if errors:
            for msg in errors:
                flash(msg, "danger")  
            return redirect(url_for("upload"))

# creating a session to store purpose and category.
session["purpose"] = purpose
session["category"] = category
