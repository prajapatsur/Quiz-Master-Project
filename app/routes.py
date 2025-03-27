from app import create_app, db, login_manager
from flask import Flask, render_template, request, redirect, url_for, flash, session
from app.forms import RegisterForm, LoginForm, SubjectForm, ChapterForm, QuizForm, QuestionForm
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
        #creating database
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
            print("Admin already exists in the database.")

    except Exception as e:
        print(f"Error while creating database: {e}")


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")

#user login, Register, Logout
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
            if user.username=="admin@gmail.com":
                return redirect(url_for('admin_dashboard'))
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

#dashboard
@app.route("/dashboard", methods=['GET'])
@login_required
def dashboard():
    # username = session.get('username', 'User')  # Retrieve username from session
    # return render_template("dashboard.html", username=username)    #used with session['username']

    quizzes= Quiz.query.all()
    subjects= Subject.query.all()
    return render_template("dashboard.html", quizzes=quizzes, subjects=subjects)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout Successful", category='success')
    return redirect(url_for('home'))


#Admin Login
@app.route("/admin/login", methods=['GET', 'POST'])
def admin_login():
    form= LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username="admin@gmail.com").first()
        if user and user.username == form.username.data and user.check_password(form.password.data):
            login_user(user)
            flash("Admin login Successful", category='success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Username or Password", category="error")
    return render_template("admin/login.html", form=form)

#Admin Dashboard
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if current_user.username != "admin@gmail.com":
        flash("Permission required to access admin dashboard.", category="error")
        return render_template("home.html")
    quizzes= Quiz.query.all()
    return render_template("admin/dashboard.html", quizzes=quizzes)

@app.route("/admin/manage_chapters")
@login_required
def admin_manage_chapter():
    if current_user.username != "admin@gmail.com":
        flash("Permission required to manage Chapters.", category="error")
        return render_template("home.html")
    chapters= Chapter.query.all()
    return render_template("admin/manage_chapters.html", chapters=chapters)

# @app.route("/admin/manage_questions")
# @login_required
# def admin_manage_question():
#     if current_user.username != "admin@gmail.com":
#         flash("Permission required to Manage Questions.", category="error")
#         return render_template("home")
#     all_questions= Question.query.all()
#     return render_template("admin/manage_questions.html", questions=all_questions)

#Managing Questions of particular quiz only. 
@app.route("/admin/manage_quiz_questions/<int:qid>")
@login_required
def admin_manage_quiz_question(qid):
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Manage Questions.", category="error")
        return render_template("home")
    
    #fetching quiz
    quiz= Quiz.query.get_or_404(qid)
    all_questions= quiz.questions
    return render_template("admin/manage_questions.html", questions=all_questions, quiz=quiz)

@app.route("/admin/manage_quizzes")
@login_required
def admin_manage_quiz():
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Manage Quiz.", category="error")
        return render_template("home")
    quizzes= Quiz.query.all()
    return render_template("admin/manage_quizzes.html", quizzes=quizzes)

@app.route("/admin/manage_subjects")
@login_required
def admin_manage_subject():
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Manage Subjects.", category="error")
        return render_template("home")
    subjects= Subject.query.all()

    return render_template("admin/manage_subjects.html", subjects=subjects)

@app.route("/admin/manage_users")
@login_required
def admin_manage_user():
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Manage Users.", category="error")
        return render_template("home")
    users= User.query.all()
    return render_template("admin/manage_users.html", users=users)


#add, edit and delete subject
@app.route("/admin/add_subject", methods=['GET', 'POST'])
@login_required
def admin_add_subject():
    form=SubjectForm()
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Add Subject.", category="error")
        return redirect(url_for('home'))
    if form.validate_on_submit():
        subject= Subject(
                name= form.name.data,
                description= form.description.data
            )
        db.session.add(subject)
        db.session.commit()
        flash("Subject added successfully!", category='success')
        return redirect(url_for('admin_manage_subject'))
    
    return render_template("admin/add_subject.html", form=form)

@app.route("/admin/edit_subject/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_subject(id):
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Edit Subject.", category="error")
        return redirect(url_for('home'))
    
    subject= Subject.query.get_or_404(id)
    form= SubjectForm(obj=subject)
    if form.validate_on_submit():
        subject.name= form.name.data
        subject.description= form.description.data
        db.session.commit()
        flash("Subject updated successfully!", category='success')
        return redirect(url_for('admin_manage_subject'))
    return render_template("admin/edit_subject.html", form=form)

@app.route("/admin/delete_subject/<int:id>", methods=['POST', 'GET'])
@login_required
def admin_delete_subject(id):
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Delete Subject.", category="error")
        return redirect(url_for('home'))
    
    subject= Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash("Subject deleted successfully!", category='success')
    return redirect(url_for('admin_manage_subject'))

#add, edit and delete chapter
@app.route("/admin/add_chapter", methods=['GET', 'POST'])
@login_required
def admin_add_chapter():
    form=ChapterForm()
    if current_user.username != "admin@gmail.com":
        flash("Permission required to Add Chapter.", category="error")
        return redirect(url_for('home'))
    
    form.subject_id.choices = [(sub.id, sub.name) for sub in Subject.query.all()]
    if form.validate_on_submit():
        chapter= Chapter(
                name= form.name.data,
                description= form.description.data,
                subject_id= form.subject_id.data
            )
        db.session.add(chapter)
        db.session.commit()
        flash("Chapter added successfully!", category='success')
        return redirect(url_for('admin_manage_chapter'))
    
    return render_template("admin/add_chapter.html", form=form)

@app.route("/admin/edit_chapter/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_chapter(id):
    if current_user.username != "admin@gmail.com":
        flash("You don't have permission to access this page", category="error")
        return redirect(url_for("home"))
    chapter = Chapter.query.get_or_404(id)
    form = ChapterForm(obj=chapter)
    form.subject_id.choices = [(sub.id, sub.name) for sub in Subject.query.all()]
    if form.validate_on_submit():
        chapter.name = form.name.data
        chapter.description = form.description.data
        chapter.subject_id = form.subject_id.data
        db.session.commit()
        flash("Chapter updated successfully!", category="success")
        return redirect(url_for("admin_manage_chapter"))
    return render_template("admin/edit_chapter.html", form=form)

@app.route("/admin/delete_chapter/<int:id>", methods=['GET','POST'])    #I realised that this get is needed here
@login_required
def admin_delete_chapter(id):
    if current_user.username != "admin@gmail.com":
        flash("Permission required to delete chapter!", category="error")
        return redirect(url_for("home"))
    chapter = Chapter.query.get_or_404(id)
    db.session.delete(chapter)
    db.session.commit()
    flash("Chapter deleted successfully!", category="success")
    return redirect(url_for("admin_manage_chapter"))


#add, edit and delete quiz
@app.route("/admin/add_quiz", methods=['GET', 'POST'])
@login_required
def admin_add_quiz():
    if current_user.username!= "admin@gmail.com":
        flash("Permission required to Add Quiz.", category="error")
        return redirect(url_for('home'))
    form= QuizForm()
    form.chapter_id.choices= [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
         quiz= Quiz(
             name= form.name.data,
             date_of_quiz= form.date_of_quiz.data,
             time_duration= form.time_duration.data,
             chapter_id= form.chapter_id.data
         )
         db.session.add(quiz)
         db.session.commit()
         flash("Quiz added!", category='success')
         return redirect(url_for('admin_manage_quiz'))
    return render_template("admin/add_quiz.html", form=form)

@app.route("/admin/edit_quiz/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_edit_quiz(id):
    if current_user.username!= "admin@gmail.com":
        flash("Permission required to Edit Quiz.", category="error")
        return redirect(url_for('home'))
    
    quiz= Quiz.query.get_or_404(id)
    form= QuizForm(obj=quiz)
    form.chapter_id.choices= [(c.id, c.name) for c in Chapter.query.all()]
    if form.validate_on_submit():
        quiz.name= form.name.data
        quiz.date_of_quiz= form.date_of_quiz.data
        quiz.time_duration= form.time_duration.data
        quiz.chapter_id= form.chapter_id.data
        db.session.commit()
        flash("Quiz updated!", category='success')
        return redirect(url_for('admin_manage_quiz'))
    return render_template("admin/edit_quiz.html", form=form)

@app.route("/admin/delete_quiz/<int:id>", methods=['POST','GET'])
@login_required
def admin_delete_quiz(id):
    if current_user.username!= "admin@gmail.com":
        flash("Permission required to Add Quiz.", category="error")
        return redirect(url_for('home'))
    quiz= Quiz.query.get_or_404(id)
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted!", category='success')
    return redirect(url_for('admin_manage_quiz'))

#add, edit and delete questions of specific quiz
#qid stands for 'quiz_id'
@app.route("/admin/add_question/<int:qid>", methods=['GET', 'POST'])
@login_required
def admin_add_question(qid):
    if current_user.username!="admin@gmail.com":
        flash('Permission required!', category='error')
        return redirect(url_for("home"))
    
    form= QuestionForm()
    if form.validate_on_submit():
        question = Question(
            question_statement=form.question_statement.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            correct_option=form.correct_option.data,
            quiz_id=qid
        )
        db.session.add(question)
        db.session.commit()
        flash(f"Question added successully to Quiz-id {qid}", category="success")
        return redirect(url_for('admin_manage_quiz_question', qid=qid))
    quiz= Quiz.query.get_or_404(qid)
    return render_template("admin/add_question.html", form=form, quiz= quiz)

@app.route("/admin/edit_quiz_question/<int:qid>/<int:question_id>")
@login_required
def admin_edit_quiz_question(qid, question_id):
    if current_user.username!="admin@gmail.com":
        flash('Permission required!', category='error')
        return redirect(url_for("home"))
    
    quiz= Quiz.query.get_or_404(qid)
    question= Question.query.get_or_404(question_id)
    form= QuestionForm(obj= question)
    if form.validate_on_submit:
        question.question_statement= form.question_statement.data
        question.option1= form.option1.data
        question.option2= form.option2.data
        question.option3= form.option3.data
        question.option4= form.option4.data
        question.correct_option= form.correct_option.data
        question.quiz_id= qid
        db.session.commit()
        flash("Quiz questions updated!", category='success')
        return redirect(url_for('admin_manage_quiz_question', qid=qid))
    
    return render_template("admin/edit_question.html", form=form, quiz=quiz)



@app.route("/quiz/<int:qid>", methods=['GET', 'POST'])
@login_required
def attempt_quiz(qid):
    quiz= Quiz.query.get_or_404(qid)
    Questions= quiz.questions
    user= User.query.get_or_404(current_user.id)
    if request.method=='POST':
        score=0
        for question in Questions:
            user_answer= request.form.get(f"question_{question.id}")
            if user_answer and int(user_answer)==question.correct_option:
                score= score+1   #for correct option user will get +1
            
        user_score= Score(
            total_scored= score,
            quiz_id= qid,
            user_id= current_user.id
        )

        db.session.add(user_score)
        db.session.commit()
        flash(f"Your score is {score}", category="success")
        return redirect(url_for("quiz_result", qid= qid, user_id= current_user.id))
    return render_template("attempt_quiz.html", quiz=quiz, questions=Questions, user=user)    

@app.route("/quiz_results/<int:qid>/<int:user_id>")
@login_required
def quiz_result(qid, user_id):
    quiz= Quiz.query.get_or_404(qid)
    user= User.query.get_or_404(user_id)
    #I could print the whole scores in that quiz by the same user.
    scores= Score.query.filter_by(quiz_id= qid, user_id= user_id)
    return render_template("quiz_result.html", quiz= quiz, score=scores, user=user)

@app.route("/results/<int:user_id>")
@login_required
def results(user_id):
    scores= Score.query.filter_by(user_id=user_id)
    return render_template("results.html", score=scores)
    