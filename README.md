# SKIS final project CS50 Introduction to Computer Sciense course
YouTube video https://youtu.be/_q5uOYQF340
>CS, python, flask, flask web framework, web development, CS50

## Technology Stack

### Backend
- **Python 3.x**: Core programming language
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Flask-WTF**: Form handling and validation
- **Werkzeug**: Password hashing and security utilities

### Frontend
- **HTML5**: Markup structure
- **CSS3**: Styling and layout
- **Jinja2**: Template engine
- **JavaScript**: Client-side interactions (if implemented)

### Database
- **SQLite**: Relational database management system
- **SQLAlchemy**: Database abstraction layer

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (recommended)

### Installation Steps

1.  Clone or Download the Application

    --bash--
    git clone <repository-url>
    cd case-management-system

2.  Create Virtual Environment

    --bash--
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3.  Install Dependencies

    --bash--
    pip install flask flask-sqlalchemy flask-wtf werkzeug

4.  Initialize Database

    --bash--
    python -c "
    from app import app, db
    with app.app_context():
        db.create_all()
        print('Database initialized successfully')
    "
5.  Run the Application

    --bash--
    python app.py
    Access the Application
    Open your browser and navigate to http://localhost:5000

## Explaining the project and the database

A comprehensive Flask-based web application for registering donation of used skis and snowboards
managing and tracking cases with user authentication, file upload capabilities, and a robust database system.

The Case Management System is a full-stack web application built with Python Flask that allows users to create, manage, and track cases.
The system features user authentication, secure file uploads, and an intuitive interface for case management.
Users can create cases, adopt existing ones, and maintain separate views for their created and selected cases.

### Sqlachemy and sqlite3:

Database structure:

1. users table.
    Required information
    id, username, hash (for password) and email,
    id is a primary key.

2. table cases table.
    Required information
    person_id, case_id, adress, email, description, reason, photo.
    person_id is a foreign key.

3. selectedcases table
    Required information
    Many-to-Many relationship: Multiple users can select multiple cases (through selectedCases junction table)
    One person might have many cases likewise one case might have many peoples interested

### Project Structure
case-management-system/
├── app.py                 # Main application file
├── users.db              # SQLite database (created automatically)
├── static/
│   ├── images/           # Uploaded images storage
│   │   └── users/        # User-uploaded files
│   └── css/              # Stylesheets (if any)
├── templates/
│   ├── index.html        # Main dashboard
│   ├── login.html        # Login page
│   ├── register.html     # Registration page
│   ├── giveRecord.html   # Case creation form
│   └── get.html          # Case adoption page
└── README.md             # This file

### Storing images of your skis and validations.

The application handles image uploads with comprehensive validation to ensure security, proper storage, and database integrity.
Here's the complete process:

Image Storage Architecture
    Storage Location

        app.config['UPLOAD_FOLDER'] = './static/images/users/'
        Path: static/images/users/ directory

Organization: All user-uploaded images stored in a single directory

    Static Serving: Images served through Flask's static file handling

    Database Storage

        class Case(db.Model):
        filename = db.Column(db.String(255))  # Stores only the filename, not full path

Form Validation (Client-Side + Server-Side)
    FlaskForm Definition:
        class formUploadImage(FlaskForm):
        image = FileField(validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Only images! .jpg, .jpeg, .png')])

    Supported Formats:JPEG (.jpg, .jpeg),PNG (.png)

## YOUTUBE Demonstration
My Final Project (https://youtu.be/_q5uOYQF340)

## About CS50
CS50 is a openware course from Havard University taught by David J. Malan

Introduction to the intellectual enterprises of computer science and the art of programming. This course teaches students how to think algorithmically and solve problems efficiently. Topics include abstraction, algorithms, data structures, encapsulation, resource management, security, and software engineering. Languages include C, Python, and SQL plus students’ choice of: HTML, CSS, and JavaScript (for web development).

Thank you for all CS50.

- Where I get CS50 course?
https://cs50.harvard.edu/x/2020/

