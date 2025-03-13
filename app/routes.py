from app import create_app, db, login_manager
from flask import Flask, render_template, request, redirect, url_for, flash, session
from app.forms import RegisterForm, LoginForm
from app.models import User, Subject, Chapter, Quiz, Question, Score
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# from app.models.chapter import Chapter
# from app.models.question import Question
# from app.models.quiz import Quiz
# from app.models.score import Score
# from app.models.subject import Subject
# from app.models.user import User

app=create_app()

@app.cli.command("db-create")
def create_db():
    try:
        print("Creating database...")
        db.create_all()
        print("Database tables created successfully!")

        # Creating admin user
        admin = User.query.filter_by(username='admin@gmail.com').first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username="admin@gmail.com",
                fullname="Admin",
                qualification="BS",
                dob=datetime.strptime("2002-03-30", "%Y-%m-%d").date()  # Convert string to date
            )
            admin.set_password("admin123")  
            db.session.add(admin)
            db.session.commit()
            print("Admin created successfully!")
        else:
            print("Admin already exists!")

    except Exception as e:
        print(f"Error creating database: {e}")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", category='danger')
            return redirect(url_for('login'))
        elif user and user.check_password(form.password.data):
            login_user(user)
            flash("Login Successful", category='success')
            return redirect(url_for('dashboard'))
    return render_template("login.html", form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form=RegisterForm()
    if form.validate_on_submit(): 
        user = User(
                    username = form.username.data,
                    fullname = form.fullname.data,
                    qualification = form.qualification.data,
                    dob = form.dob.data
                )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Registration Successful", category='success')        
        return redirect(url_for('login'))
    return render_template("register.html", form=form)

@app.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    username = session.get('username', 'User')  # Retrieve username from session
    # return render_template("dashboard.html", username=username)    #used with session['username']
    return render_template("dashboard.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successful", category='success')
    return redirect(url_for('home'))