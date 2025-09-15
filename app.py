import os

from flask import flash, Flask, render_template, request,  session, redirect
from login import login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from werkzeug.utils import secure_filename

# https://flask-wtf.readthedocs.io/en/stable/form.html#module-flask_wtf.file
# flask-wtf for the forms and upload
# pip install flask-wtf
# !!! pip install Flask-SQLAlchemy !!!

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate random secret key for session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # data base in file users.db
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = './static/images/'

# Check the available file format
class formUploadImage(FlaskForm):
    # create a field
    image = FileField(validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Only images! .jpg, .jpeg, .png')])

# Initiate Data Base
db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    cases = db.relationship('Case', backref='person', lazy=True)

class Case(db.Model):
    __tablename__ = 'cases'

    id_case = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    location = db.Column(db.String(255))
    description = db.Column(db.String(255))
    email = db.Column(db.String(255))
    filename = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id_case': self.id_case,
            'person_id': self.person_id,
            'location': self.location,
            'description': self.description,
            'email': self.email,
            'filename': self.filename
        }

class SelectedCase(db.Model):
    __tablename__ = 'selectedCases'
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    id_case = db.Column(db.Integer, db.ForeignKey('cases.id_case'), index=True)

    # Add unique constraint
    __table_args__ = (
        db.UniqueConstraint('person_id', 'id_case', name='_person_case_uc'),
    )

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

@app.after_request
def after_request(response):
    response.headers['Cache-Control']='no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'
    return response

@app.route('/')
@login_required
def index():
    try:
        if 'user_id' not in session:
            return redirect('/login')

        user_id = session['user_id']

        # Get all cases connected with user
        rowsMy = Case.query.filter_by(person_id=user_id).all()

        # Get all selected cases by user
        rowsSelected = db.session.query(Case)\
            .join(SelectedCase, SelectedCase.id_case == Case.id_case)\
            .filter(SelectedCase.person_id == user_id)\
            .all()

        # Get user name
        user = User.query.get(user_id)
        if not user:
            flash("User not found")
            return redirect('/login')

        # Transform to list of dictionaries
        rowsMy = [case.to_dict() for case in rowsMy] if rowsMy else []
        rowsSelected = [case.to_dict() for case in rowsSelected] if rowsSelected else []

        return render_template('index.html',
                            rowsMy=rowsMy,
                            rowsSelected=rowsSelected,
                            name=user.username)

    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        flash("An error occurred while loading the page")
        return redirect('/login')

@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    try:
        if 'user_id' not in session:
            return redirect('/login')

        user_id = session['user_id']

        # Fetch the selected case
        selected_case = SelectedCase.query.filter_by(
            person_id=user_id,
            id_case=id
        ).first()

        if not selected_case:
            flash("Selected case not found.")
            return redirect('/')

        # Remove the selected case record
        db.session.delete(selected_case)
        db.session.commit()

        flash("Selected case successfully removed.")
        return redirect('/')

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting case: {str(e)}")
        flash("An error occurred while deleting the case")
        return redirect('/')

@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Get user by name
        user = User.query.filter_by(username=username).first()  # Request by SQLAlchemy

        if user and check_password_hash(user.password, password):
            # If user found and password matches
            session["user_id"] = user.id
            flash("Login successful!")
            return redirect("/")
        else:
            flash("Invalid username or password!")  # Show error
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        error = None
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        passConf = request.form.get("passConf")

        # Check the existing user
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = "Email already registered!"

        # Check password match
        if password != passConf:
            error = "Passwords don't match"

        # If not error, hash the password
        if error is None:
            hashed_password = generate_password_hash(password)

            # Add new user to data base
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()

            # Create user session
            session["user_id"] = new_user.id

            flash("Registration successful!")
            return redirect("/login")

        if error:
            flash(error)
        return redirect('/register')

    return render_template("register.html")

@app.route('/give', methods=['GET', 'POST'])
@login_required
def registerGive():
    form = formUploadImage()
    if request.method == 'POST':
        f = form.image.data
        location = request.form.get('location')
        description = request.form.get('description')

        if 'user_id' not in session:
            flash("You must be logged in to access this page")
            return redirect('/login')

        user = session['user_id']

        # Fetch the user record using SQLAlchemy
        user_record = db.session.query(User).filter(User.id == user).first()
        if user_record:
            email = user_record.email
        else:
            flash('User not found')
            return redirect('/login')

        if f:
            filename = secure_filename(f.filename)

            # Check if the file already exists using ORM
            existing_file = db.session.query(Case).filter(Case.filename == filename).first()
            if existing_file:
                flash('Filename already exists! Please rename the file and try again.')
                return redirect('/give')

            # Save the file
            file_path = os.path.join('static/images/users/', filename)
            f.save(file_path)

            # Insert new case record into the database
            new_case = Case(person_id=user, location=location, email=email, description=description, filename=filename)
            db.session.add(new_case)
            db.session.commit()
            print(f"Added case: {new_case}")

            return redirect('/')

        else:
            filename = 'default.jpg'

            # Insert new case with default filename
            new_case = Case(person_id=user, location=location, email=email, description=description, filename=filename)
            db.session.add(new_case)
            db.session.commit()
            print(f"Added case: {new_case}")

    return render_template('giveRecord.html', form=form)

@app.route('/get')
@login_required
def get():
    try:
        if 'user_id' not in session:
            return redirect('/login')

        user_id = session['user_id']

        # Fetch all cases NOT selected by the current user
        subquery = db.session.query(SelectedCase.id_case)\
            .filter(SelectedCase.person_id == user_id)\
            .subquery()

        allrows = Case.query\
            .filter(Case.person_id != user_id)\
            .filter(~Case.id_case.in_(subquery))\
            .all()

        return render_template('get.html', allrows=allrows, user_id=user_id)

    except Exception as e:
        app.logger.error(f"Error in adopt route: {str(e)}")
        flash("An error occurred while loading cases")
        return redirect('/')

@app.route('/rec/<int:id>', methods=['POST'])
@login_required
def getRecord(id):
    try:
        if 'user_id' not in session:
            return redirect('/login')

        user_id = session['user_id']

        # Check if the case exists
        case = Case.query.get(id)
        if not case:
            flash("Case not found.")
            return redirect('/get')

        # Ensure the user doesn't adopt their own case
        if case.person_id == user_id:
            flash("You cannot adopt your own case.")
            return redirect('/get')

        # Check if already adopted
        existing = SelectedCase.query.filter_by(
            person_id=user_id,
            id_case=id
        ).first()

        if existing:
            flash("You've already adopted this case")
            return redirect('/get')

        # Add adoption record
        adopted_case = SelectedCase(
            person_id=user_id,
            id_case=case.id_case
        )
        db.session.add(adopted_case)
        db.session.commit()

        flash("Case successfully adopted!", "success")
        return redirect('/')

    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adopting case: {str(e)}")
        flash("An error occurred while adopting the case")
        return redirect('/get')


# Initiate new session if does not exist
if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Create table in data base
    app.run(debug=True)
