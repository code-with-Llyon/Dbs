from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "gnib-school-project-key"

# adding the upload logic and determining the file type
# that is acceptable and the maximum size it should take.
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 5

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
