from app import create_app, db, login_manager
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from app.forms import RegisterForm, LoginForm, SubjectForm, ChapterForm, QuizForm, QuestionForm
from app.models import User, Subject, Chapter, Quiz, Question, Score
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import or_, and_
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
# from app.models.chapter import Chapter
# from app.models.question import Question
# from app.models.quiz import Quiz
# from app.models.score import Score
# from app.models.subject import Subject
# from app.models.user import User

load_dotenv()

app = create_app()

# Ensure login manager is properly initialized
login_manager.init_app(app)
            
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.cli.command("db-create")
def create_db():
    try:
        #creating database
        print("Creating database...")
        db.create_all()
        print("Database tables created successfully!")

        # Creating admin user
        admin = User.query.filter_by(username=os.getenv('admin_username')).first()
        if not admin:
            print("Creating admin user...")
            admin = User(
                username=os.getenv('admin_username'),
                fullname=os.getenv('admin_fullname'),
                qualification=os.getenv('admin_qualification'),
                dob=datetime.strptime("2002-03-30", "%Y-%m-%d").date()  # Convert string to date
            )
            admin.set_password(os.getenv('admin_password'))  
            db.session.add(admin)
            db.session.commit()
            print("Admin created successfully!")
        else:
            print("Admin already exists in the database.")

    except Exception as e:
        print(f"Error while creating database: {e}")



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
            if user.username==os.getenv('admin_username'):
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

#User_dashboard
@app.route("/dashboard", methods=['GET','POST'])
@login_required
def dashboard():
    # username = session.get('username', 'User')  # Retrieve username from session
    # return render_template("dashboard.html", username=username)    #used with session['username']

    #leaderboard
    users= User.query.filter(User.username != os.getenv('admin_username')).all()
    leaderboard_data=[]

    for user in users:
        scores= Score.query.filter_by(user_id=user.id).all()
        total_scored= sum([s.total_scored for s in scores])
        leaderboard_data.append({
            "user_fullname": user.fullname,
            "score": total_scored
        })
    leaderboard_data.sort(key=lambda x: x['score'], reverse=True)
    fullnames= [x["user_fullname"] for x in leaderboard_data]
    user_total_scores= [x["score"] for x in leaderboard_data]  

    quizzes= Quiz.query.all()
    subjects= Subject.query.all()
    chapters= Chapter.query.all()
    scores= Score.query.filter_by(user_id=current_user.id).all()

    #average score
    total_attempted_quizzes= len(scores)
    if total_attempted_quizzes>0:
        average_score= sum([s.total_scored for s in scores])/total_attempted_quizzes
    else:
        average_score= 0

    #search feature
    query= request.form.get("query","")
    if request.method=="POST":
        subjects= Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
        quizzes= Quiz.query.filter(Quiz.name.ilike(f'%{query}%')).all()
        chapters= Chapter.query.filter(or_(Chapter.name.ilike(f'%{query}%'), Chapter.description.ilike(f'%{query}%'))).all()
    return render_template("dashboard.html",
                           quizzes=quizzes,
                           subjects=subjects,
                           chapters=chapters,
                           scores=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score,
                           leaderboard_data=leaderboard_data,
                           fullnames=fullnames,
                           user_total_scores=user_total_scores)

#User Chapter view for specific subject-id
@app.route("/view_chapters/<int:sid>", methods=['POST','GET'])
@login_required
def view_chapters(sid):
    chapters= Chapter.query.filter_by(subject_id=sid)
    query= request.form.get("query","")

    if request.method=="POST":
        chapters= Chapter.query.filter(and_(Chapter.subject_id==sid),or_(Chapter.name.ilike(f"%{query}%"),Chapter.description.ilike(f"%{query}%"))).all()
    return render_template("view_chapters.html", chapters=chapters, sid=sid)

#User Quiz View for specific chapter-id
@app.route("/view_quiz/<int:cid>", methods=['GET','POST'])
@login_required
def view_quizzes(cid):
    quizzes= Quiz.query.filter_by(chapter_id=cid)

    query= request.form.get("query","")
    if request.method=="POST":
        quizzes= Quiz.query.filter(and_(Quiz.chapter_id==cid), Quiz.name.ilike(f"%{query}%")).all()
    return render_template("view_quizzes.html", quizzes=quizzes, cid=cid)

#user logout
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
        user = User.query.filter_by(username=os.getenv('admin_username')).first()
        if user and user.username == form.username.data and user.check_password(form.password.data):
            login_user(user)
            flash("Admin login Successful", category='success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid Username or Password", category="error")
    return render_template("admin/login.html", form=form)

#Admin Dashboard
@app.route("/admin/dashboard", methods=['GET','POST'])
@login_required
def admin_dashboard():
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to access admin dashboard.", category="error")
        return render_template("home.html")
    quizzes= Quiz.query.all()
    quiz_names = [quiz.name for quiz in quizzes]
    average_scores = []
    completion_rates = []

    for quiz in quizzes:
        scores = Score.query.filter_by(quiz_id=quiz.id).all()
        if scores:
            average_score = sum([s.total_scored for s in scores]) / len(scores)

            users_attempted = len(scores)
            completion_rate = (users_attempted / (User.query.count() - 1)) * 100
        else:
           average_score = 0 
           completion_rate = 0
        average_scores.append(average_score)
        completion_rates.append(completion_rate)

    #search feature
    query= request.form.get("query","")
    if request.method=="POST":
        quizzes= Quiz.query.filter(or_(Quiz.name.ilike(f"%{query}%"), Quiz.chapter_id.ilike(f"%{query}%"))).all()

    return render_template("admin/dashboard.html",
                           quizzes=quizzes,
                           quiz_names=quiz_names,
                           average_scores=average_scores,
                           completion_rates=completion_rates
                        )

#Admin Manages
@app.route("/admin/manage_subjects", methods=['GET','POST'])
@login_required
def admin_manage_subject():
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to Manage Subjects.", category="error")
        return render_template("home")
    subjects= Subject.query.all()

    query= request.form.get("query","")

    if request.method=="POST":
        subjects= Subject.query.filter(or_(Subject.name.ilike(f"%{query}%"), Subject.description.ilike(f"%{query}%"))).all()

    return render_template("admin/manage_subjects.html", subjects=subjects, query=query)

@app.route("/admin/manage_chapters", methods=['GET','POST'])
@login_required
def admin_manage_chapter():
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to manage Chapters.", category="error")
        return render_template("home.html")
    chapters= Chapter.query.all()

    query= request.form.get("query","")

    if request.method=="POST":
        chapters= Chapter.query.filter(or_(Chapter.name.ilike(f"%{query}%"),Chapter.description.ilike(f"%{query}%"),Chapter.subject_id.ilike(f"%{query}%"))).all()
    return render_template("admin/manage_chapters.html", chapters=chapters)

@app.route("/admin/manage_quizzes", methods=['GET','POST'])
@login_required
def admin_manage_quiz():
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to Manage Quiz.", category="error")
        return render_template("home")
    quizzes= Quiz.query.all()
    query= request.form.get("query","")

    if request.method=="POST":
        quizzes= Quiz.query.filter(or_(Quiz.name.ilike(f"%{query}%"), Quiz.chapter_id.ilike(f"%{query}%"))).all()
    return render_template("admin/manage_quizzes.html", quizzes=quizzes)

@app.route("/admin/manage_users", methods=['GET','POST'])
@login_required
def admin_manage_user():
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to Manage Users.", category="error")
        return render_template("home")
    users= User.query.all()

    query= request.form.get("query","")

    if request.method=="POST":
        users= User.query.filter(or_(User.fullname.ilike(f"%{query}%"), User.username.ilike(f"%{query}%"))).all()
    return render_template("admin/manage_users.html", users=users)

#Managing Questions of particular quiz only. 
@app.route("/admin/manage_quiz_questions/<int:qid>")
@login_required
def admin_manage_quiz_question(qid):
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to Manage Questions.", category="error")
        return render_template("home")
    
    #fetching quiz
    quiz= Quiz.query.get_or_404(qid)
    all_questions= quiz.questions
    return render_template("admin/manage_questions.html", questions=all_questions, quiz=quiz)

#subject ke pas chapter pe click karke yaha redirect ho jayenge and subject specific chapters dekh payenge
@app.route("/admin/view_chapter/<int:sid>")
@login_required
def admin_view_chapter(sid):
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required!", category="error")
        return render_template("home.html")
    chapters= Chapter.query.filter_by(subject_id=sid)
    chapter_quiz_count = {chapter.id: Quiz.query.filter_by(chapter_id=chapter.id).count() for chapter in chapters}
    return render_template("admin/admin_view_chapter.html", chapters=chapters, sid=sid, chapter_quiz_count=chapter_quiz_count)

#admin_view_quiz--> Admin can view quizzes for specific chapter
@app.route("/admin/view_quiz/<int:cid>")
@login_required
def admin_view_quiz(cid):
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required!", category="error")
        return render_template("home.html")
    quizzes= Quiz.query.filter_by(chapter_id=cid).all()
    return render_template("admin/admin_view_quiz.html", cid=cid, quizzes=quizzes)

@app.route("/admin/view_result/<int:qid>")
@login_required
def admin_view_result(qid):
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required!", category="error")
        return render_template("home.html")
    results= Score.query.filter_by(quiz_id=qid).all()
    quiz= Quiz.query.filter_by(id=qid).first()
    return render_template("admin/admin_view_result.html", scores=results, quiz=quiz)

@app.route("/quiz_results/<int:qid>/<int:user_id>")
@login_required
def quiz_result(qid, user_id):
    quiz= Quiz.query.get_or_404(qid)
    user= User.query.get_or_404(user_id)
    #I could print the whole scores in that quiz by the same user.
    scores= Score.query.filter_by(quiz_id= qid, user_id= user_id)
    return render_template("quiz_result.html", quiz= quiz, score=scores, user=user)

#Result of user
@app.route("/results/<int:user_id>", methods=['GET','POST'])
@login_required
def results(user_id):
    scores= Score.query.filter_by(user_id=user_id).all()
    total_attempted_quizzes= len(scores)
    if total_attempted_quizzes>0:
        average_score= sum([s.total_scored for s in scores])/total_attempted_quizzes
    else:
        average_score= 0
    return render_template("results.html",
                           score=scores,
                           total_attempted_quizzes=total_attempted_quizzes,
                           average_score=average_score
                        )

#add, edit and delete subject
@app.route("/admin/add_subject", methods=['GET', 'POST'])
@login_required
def admin_add_subject():
    form=SubjectForm()
    if current_user.username != os.getenv('admin_username'):
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
    if current_user.username != os.getenv('admin_username'):
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
    if current_user.username != os.getenv('admin_username'):
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
    if current_user.username != os.getenv('admin_username'):
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
    if current_user.username != os.getenv('admin_username'):
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

@app.route("/admin/delete_chapter/<int:id>", methods=['GET', 'POST'])
@login_required
def admin_delete_chapter(id):
    if current_user.username != os.getenv('admin_username'):
        flash("Permission required to delete chapter!", category="error")
        return redirect(url_for("home"))

    chapter = Chapter.query.get_or_404(id)
    quizzes = Quiz.query.filter_by(chapter_id=id).all()
    for quiz in quizzes:
        Question.query.filter_by(quiz_id=quiz.id).delete()
        db.session.delete(quiz)
    db.session.delete(chapter)
    db.session.commit()

    flash("Chapter and its associated quizzes deleted successfully!", category="success")
    return redirect(url_for("admin_manage_chapter"))



#add, edit and delete quiz
@app.route("/admin/add_quiz", methods=['GET', 'POST'])
@login_required
def admin_add_quiz():
    if current_user.username!= os.getenv('admin_username'):
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
    if current_user.username!= os.getenv('admin_username'):
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
    if current_user.username!= os.getenv('admin_username'):
        flash("Permission required to Add Quiz.", category="error")
        return redirect(url_for('home'))
    quiz= Quiz.query.get_or_404(id)

    questions= Question.query.filter_by(quiz_id=id).delete()
    db.session.delete(quiz)
    db.session.commit()
    flash("Quiz deleted!", category='success')
    return redirect(url_for('admin_manage_quiz'))

#add, edit and delete questions of specific quiz
#qid stands for 'quiz_id'
@app.route("/admin/add_question/<int:qid>", methods=['GET', 'POST'])
@login_required
def admin_add_question(qid):
    if current_user.username!=os.getenv('admin_username'):
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

@app.route("/admin/edit_quiz_question/<int:qid>/<int:question_id>", methods=['GET','POST'])
@login_required
def admin_edit_quiz_question(qid, question_id):
    if current_user.username!=os.getenv('admin_username'):
        flash('Permission required!', category='error')
        return redirect(url_for("home"))
    
    quiz= Quiz.query.get_or_404(qid)
    question= Question.query.get_or_404(question_id)
    form= QuestionForm(obj= question)
    if form.validate_on_submit():
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

@app.route("/admin/delete_quiz_question/<int:qid>/<int:question_id>", methods=['GET','POST'])
@login_required
def admin_delete_quiz_question(qid, question_id):
    if current_user.username!=os.getenv('admin_username'):
        flash('Permission required!', category='error')
        return redirect(url_for("home"))
    
    quiz= Quiz.query.get_or_404(qid)
    question= Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash("Question deleted!", category='success')
    return redirect(url_for('admin_manage_quiz_question', qid=qid))

#Attempt Quiz
@app.route("/quiz/<int:qid>", methods=['GET', 'POST'])
@login_required
def attempt_quiz(qid):
    quiz= Quiz.query.get_or_404(qid)
    Questions= quiz.questions
    user= User.query.get_or_404(current_user.id)

    current_time = datetime.now()
    start_time = quiz.date_of_quiz
    end_time = start_time + timedelta(minutes=quiz.time_duration)

    # Check if current time is within the allowed time window
    if not (start_time <= current_time <= end_time):
        flash(f"Quiz is only available between {start_time} and {end_time}.", category="error")
        return redirect(url_for("dashboard"))

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


    
#User Select Quiz 
@app.route("/quiz", methods=['GET','POST'])
@login_required
def select_quiz():
    subjects = Subject.query.all()
    chapters = Chapter.query.all()
    quizzes = Quiz.query.all()

    # if request.method == 'POST':
    #     subject_id = request.form.get('subject_id')
    #     chapter_id = request.form.get('chapter_id')

    #     if subject_id:
    #         quizzes = Quiz.query.join(Chapter).filter(Chapter.subject_id == subject_id).all()
    #     if chapter_id:
    #         quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

    query= request.form.get("query","")
    if request.method=="POST":
        quizzes= Quiz.query.filter(Quiz.name.ilike(f"%{query}%")).all()
    return render_template("all_quiz.html",
                        subjects=subjects,
                        chapters=chapters,
                        quizzes=quizzes
                    )


#API Endpoints
@app.route("/api/subject")
def get_subjects():
    subjects= Subject.query.all()
    subject_list=[]
    for sub in subjects:
        subject={
                        "id": sub.id,
                        "name":sub.name,
                        "description":sub.description
        }
        subject_list.append(subject)
    return jsonify(subject_list)

@app.route("/api/quiz")
def get_quizzes():
    quizzes= Quiz.query.all()
    quiz_list=[]
    for q in quizzes:
        quiz={
                        "Id": q.id,
                        "Quiz Name":q.name,
                        "Chapter_id":q.chapter_id,
                        "Date_of_quiz":q.date_of_quiz,
                        "Time_duration":q.time_duration
        }
        quiz_list.append(quiz)
    return jsonify(quiz_list)

@app.route("/api/score")
@login_required
def get_scores():
    if current_user.username==os.getenv('admin_username'):
        scores= Score.query.all()
        score_list=[]
        for s in scores:
            quiz= s.quiz
            score={
                            "Attempt Id": s.id,
                            "Quiz Name":quiz.name,
                            "total_scored":s.total_scored,
                            "Time of attempt":s.timestamp,
                            "Date of Quiz":quiz.date_of_quiz,
                            "User ID": s.user_id
            }
            score_list.append(score)
        return jsonify(score_list)
    else:
        scores= Score.query.filter_by(user_id=current_user.id).all()
        score_list=[]
        for s in scores:
            quiz= s.quiz
            score={
                            "Attempt Id": s.id,
                            "Quiz Name":quiz.name,
                            "total_scored":s.total_scored,
                            "Time of attempt":s.timestamp,
                            "Date of Quiz":quiz.date_of_quiz
            }
            score_list.append(score)
        return jsonify(score_list)
