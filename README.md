project Name: GNIB Document Validator

  Project Overview
  
The GNIB Document Validator is a Flask-based web application that streamlines the Irish GNIB/IRP (immigration) document submission process for students and workers.
It provides structured document upload, validation, and administrative review capabilities.

Core Functionality

1 User Side:

- Purpose selection (Study/Work) with category-specific requirements (Masters, Undergraduate, Employment Permit, Graduate 1G)
- Dynamic document upload fields based on selected category
- File validation (PDF, JPG, JPEG, PNG; max 5MB)
- Passport expiry date verification
- Unique GNIB Application Code generation for tracking
- Real-time checklist showing uploaded/missing documents

2 Admin Side:

- Secure login with environment-based credentials
- Centralized dashboard displaying all submissions
- Document approval/rejection workflow
- Optional OCR text extraction from uploaded documents
- Document search

3 Technologies Used:

- Backend: Python 3, Flask, SQLite
- Frontend: HTML5, CSS, Bootstrap, JavaScript
- Security: python-dotenv for environment variables, Werkzeug for file handling
- External API: OCR.Space for document text extraction

4 Key Features:

- MVC architecture pattern
- Session-based admin authentication
- Persistent database tracking
- Unit tests for file validation and passport expiry logic
- Deployable on cPanel

5 Value Proposition:

Fast-tracks GNIB application processing by ensuring document completeness and correctness before submission, significantly reducing application delays and rejection rates. 
Simplifies the IRP Card application experience for international students and workers in Ireland by providing real-time validation, 
organized tracking, and error prevention—eliminating common submission mistakes and expediting approval timelines.
Reduces administrative burden for both applicants and immigration officers while improving application success rates through proactive document 
verification and structured submission workflows.

6 How to run:

The app can run on:
  Local machine (Flask development server)
  Python-friendly hosting (e.g., Railway, Render, VPS)
  cPanel (via Passenger WSGI or Python App Setup)

Key deployment steps include:
- Upload entire project folder
- Configure Python environment
- Install requirements
- Configure .env file on the server
- Point the WSGI file to app.py

7 Refrences:
- Flask Documentation — https://flask.palletsprojects.com
- SQLite Documentation — https://sqlite.org/docs.html
- OCR.Space API — https://ocr.space/ocrapi
- python-dotenv — https://pypi.org/project/python-dotenv
- Requests Library — https://requests.readthedocs.io
- Werkzeug File Upload Patterns — https://flask.palletsprojects.com/en/latest/patterns/fileuploads/
- chatgpt
- youtube - https://www.youtube.com/watch?v=Z1RJmh_OqeA
