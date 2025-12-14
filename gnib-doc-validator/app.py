from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import os
from datetime import datetime
from werkzeug.utils import secure_filename
import sqlite3
import string
import secrets

app = Flask(__name__)
app.secret_key = "gnib-school-project-key"

# adding the upload logic and determining the file type
# that is acceptable and the maximum size it should take.
# Upload Settings reference:  file uploads pattern.  (Flask docs upload pattern:
# https://flask.palletsprojects.com/en/latest/patterns/fileuploads/)
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 5

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# This dictionary is based on the project structure and was
# generated and structured by ChatGPT with the help of the project description.
# It is the "server truth" for which documents are required for each purpose / category.
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

# some docs like scholarship_proof are optional, so we don't force upload errors for them
OPTIONAL_DOCS = {"scholarship_proof"}

# SQLite setup (Python sqlite3 docs pattern:
# https://docs.python.org/3/library/sqlite3.html)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "gnib_uploads.db")


def get_db_connection():
    """simple helper to open sqlite connection with row factory (so we can use row['col'])"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create uploads table if it does not exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            application_code TEXT NOT NULL,
            purpose TEXT NOT NULL,
            category TEXT NOT NULL,
            doc_type TEXT NOT NULL,
            filename TEXT NOT NULL,
            expiry_date TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            uploaded_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def generate_application_code(length: int = 8) -> str:
    """Generate a simple numeric reference code like 8-digit GNIB code.
    (pattern inspired by Python secrets docs:
    https://docs.python.org/3/library/secrets.html)
    """
    digits = string.digits
    return "".join(secrets.choice(digits) for _ in range(length))


# checking if the file extension is allowed
def allowed_file(filename: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def get_required_docs(purpose: str, category: str):
    """small helper to safely read required docs from DOC_MAP"""
    return DOC_MAP.get(purpose, {}).get(category, [])


# created sessions to keep track of the selected purpose, category and uploaded documents
def ensure_session_store():
    # keeping default values in session so we don't get KeyError later
    session.setdefault("purpose", None)
    session.setdefault("category", None)
    session.setdefault("uploaded_docs", {})


# Remodified the route to fit my project
@app.route("/")
def index():
    ensure_session_store()
    return render_template("index.html")


# routing the upload document, using template
@app.route("/upload", methods=["GET", "POST"])
def upload():
    ensure_session_store()

    # pulling whatever we already have in the session
    purpose = session.get("purpose")
    category = session.get("category")
    uploaded_docs = session.get("uploaded_docs", {})
    errors = []

    if request.method == "POST":
        purpose = request.form.get("purpose")
        category = request.form.get("category")

        # Validating purpose & category
        if not purpose or purpose not in DOC_MAP:
            errors.append("Please select a valid purpose (study or work).")
        if not category or category not in DOC_MAP.get(purpose, {}):
            errors.append("Please select a valid category for that purpose.")

        required_docs = get_required_docs(purpose, category)

        # Validate each required doc's file
        # this logic is aligned with the dynamic inputs generated in validation.js
        # where each file field is like: name="document_passport" etc.
        for doc_type in required_docs:
            field_name = f"document_{doc_type}"
            file = request.files.get(field_name)
            expiry_field = f"expiry_{doc_type}"
            expiry_date = request.form.get(expiry_field)

            label = doc_type.replace("_", " ").title()

            # if file is missing
            if not file or file.filename == "":
                if doc_type in OPTIONAL_DOCS:
                    # optional doc can be skipped
                    continue
                errors.append(f"Please upload a file for {label}.")
                continue

            # checking extension
            if not allowed_file(file.filename):
                errors.append(
                    f"{label}: Only PDF, JPG, JPEG, PNG files are allowed."
                )
                continue

            # checking file size by seeking to end and back
            file.seek(0, os.SEEK_END)
            size_bytes = file.tell()
            file.seek(0)
            if size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
                errors.append(
                    f"{label}: File must be under {MAX_FILE_SIZE_MB} MB."
                )
                continue

            # Passport expiry validation
            if doc_type == "passport":
                if not expiry_date:
                    errors.append("Expiry date is required for Passport.")
                else:
                    try:
                        exp = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                        if exp <= datetime.today().date():
                            errors.append("Passport appears to be expired.")
                    except ValueError:
                        errors.append(
                            "Invalid expiry date for Passport (use YYYY-MM-DD)."
                        )

        # If there are errors, show them and stay on the same page
        if errors:
            for msg in errors:
                flash(msg, "danger")
        else:
            # Save purpose & category in session
            session["purpose"] = purpose
            session["category"] = category

            # Generate application code for this batch
            # this is stored in session so all uploads share the same reference
            application_code = session.get("application_code")
            if not application_code:
                application_code = generate_application_code()
                session["application_code"] = application_code

            # Save all files
            uploaded_docs = session.get("uploaded_docs", {})
            required_docs = get_required_docs(purpose, category)

            conn = get_db_connection()
            cur = conn.cursor()

            for doc_type in required_docs:
                field_name = f"document_{doc_type}"
                file = request.files.get(field_name)
                if not file or file.filename == "":
                    # optional or missing doc, skip saving
                    continue

                safe_name = secure_filename(file.filename)
                final_name = f"{doc_type}_{int(datetime.now().timestamp())}_{safe_name}"
                filepath = os.path.join(
                    app.config["UPLOAD_FOLDER"], final_name)
                file.save(filepath)

                expiry_field = f"expiry_{doc_type}"
                expiry_date = request.form.get(expiry_field)

                uploaded_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                uploaded_docs[doc_type] = {
                    "filename": final_name,
                    "expiry": expiry_date,
                    "uploaded_at": uploaded_at,
                }

                # Insert into SQLite with status 'pending'
                # basic INSERT pattern follows sqlite3 doc examples
                cur.execute(
                    """
                    INSERT INTO uploads
                    (application_code, purpose, category, doc_type, filename, expiry_date, status, uploaded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        application_code,
                        purpose,
                        category,
                        doc_type,
                        final_name,
                        expiry_date,
                        "pending",
                        uploaded_at,
                    ),
                )

            conn.commit()
            conn.close()

            session["uploaded_docs"] = uploaded_docs
            flash(
                f"All selected documents uploaded successfully! "
                f"Your GNIB reference code is: {application_code}",
                "success",
            )

    # Build checklist status for right-hand panel
    uploaded_docs = session.get("uploaded_docs", {})
    purpose = session.get("purpose")
    category = session.get("category")

    status_list = []
    required_docs = []
    if purpose and category:
        required_docs = get_required_docs(purpose, category)
        for doc in required_docs:
            info = uploaded_docs.get(doc)
            status_list.append({
                "doc_type": doc,
                "uploaded": bool(info),
                "info": info,
            })

    all_ready = bool(required_docs) and all(
        item["uploaded"] for item in status_list
    )

    return render_template(
        "upload.html",
        purpose=purpose,
        category=category,
        required_docs=status_list,
        all_ready=all_ready,
    )


# modified the checklist rout to better suit the project.
@app.route("/checklist")
def checklist():
    ensure_session_store()
    purpose = session.get("purpose")
    category = session.get("category")
    uploaded_docs = session.get("uploaded_docs", {})

    # created the required list
    # if purpose and category evaluates to true,
    # we add then inside the required list
    required_docs = []
    if purpose and category:
        required_docs = get_required_docs(purpose, category)

    # created the status list
    # interacting through the list and appending into the status list
    status_list = []
    for doc in required_docs:
        info = uploaded_docs.get(doc)
        status_list.append({
            "doc_type": doc,
            "uploaded": bool(info),
            "info": info,
        })

    all_ready = bool(required_docs) and all(
        item["uploaded"] for item in status_list
    )

    return render_template(
        "checklist.html",
        purpose=purpose,
        category=category,
        required_docs=status_list,
        all_ready=all_ready,
    )

# Admin section....

# this part was created by ChatGPT for the project, following basic
# Flask login + dashboard patterns:
# https://flask.palletsprojects.com/en/latest/quickstart/#sessions

# simple admin login for now (no users table yet)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    # for now admin username/password is hard-coded
    ADMIN_USER = "admin"
    ADMIN_PASS = "12345"

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            # using Flask session, same pattern used in their docs
            session["admin_logged_in"] = True
            flash("Welcome, admin.", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.", "danger")

    return render_template("admin_login.html")

# check if admin is logged in


def require_admin():
    # just returns True/False, routes will redirect if not logged in
    return bool(session.get("admin_logged_in"))


# admin dashboard route
@app.route("/admin")
def admin_dashboard():
    # if not logged in, send them to login page
    if not require_admin():
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cur = conn.cursor()

    # pulling all uploads and list them in descending order.
    cur.execute("""
        SELECT id, application_code, purpose, category,
               doc_type, filename, expiry_date, status, uploaded_at
        FROM uploads
        ORDER BY uploaded_at DESC
    """)
    uploads = cur.fetchall()
    conn.close()

    # this template will loop over "uploads" and show them in a table
    return render_template("admin_dashboard.html", uploads=uploads)

# route to approve a single document


@app.route("/admin/approve/<int:upload_id>")
def admin_approve(upload_id):
    if not require_admin():
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE uploads SET status = 'approved' WHERE id = ?",
        (upload_id,),
    )
    conn.commit()
    conn.close()

    flash("Document has been approved.", "success")
    return redirect(url_for("admin_dashboard"))


# route to reject a single document
@app.route("/admin/reject/<int:upload_id>")
def admin_reject(upload_id):
    if not require_admin():
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE uploads SET status = 'rejected' WHERE id = ?",
        (upload_id,),
    )
    conn.commit()
    conn.close()

    flash("Document has been rejected.", "warning")
    return redirect(url_for("admin_dashboard"))


# logout route for admin
@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_login"))


# API Route for JS Validation (optional, for front-end use)
# client-side validation pattern here is custom for this project,
# but the JSON response style follows the typical Flask + fetch pattern.
@app.route("/api/validate", methods=["POST"])
def api_validate():
    ensure_session_store()
    data = request.get_json() or {}

    purpose = data.get("purpose")
    category = data.get("category")
    doc_type = data.get("doc_type")
    expiry_date = data.get("expiry_date")

    errors = []

    if not purpose or purpose not in DOC_MAP:
        errors.append("Purpose is invalid.")
    if not category or category not in DOC_MAP.get(purpose, {}):
        errors.append("Category invalid.")

    required_docs = get_required_docs(purpose, category)

    if not doc_type:
        errors.append("Document type required.")
    elif required_docs and doc_type not in required_docs:
        errors.append("Document type not required for this category.")

    if doc_type == "passport":
        if not expiry_date:
            errors.append("Expiry date required for passport.")
        else:
            try:
                exp = datetime.strptime(expiry_date, "%Y-%m-%d").date()
                if exp <= datetime.today().date():
                    errors.append("Passport appears expired.")
            except ValueError:
                errors.append("Invalid expiry date format.")

    if errors:
        return jsonify({"ok": False, "errors": errors}), 400

    return jsonify({"ok": True, "message": "Valid data"})


# Run the Flask app in debug mode (from Flask quickstart pattern:
# https://flask.palletsprojects.com/en/latest/quickstart/)
if __name__ == "__main__":
    # making sure the sqlite table exists before the server starts
    init_db()
    app.run(debug=True)
