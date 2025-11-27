from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "gnib-school-project-key"
