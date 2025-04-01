# Quiz Master

## Overview
Quiz Master is an interactive web-based quiz management system designed to create, manage, and evaluate quizzes efficiently. It supports multiple users, tracks quiz performance, and provides an intuitive admin dashboard with insightful analytics.

## Features
- **User Authentication**: Secure login and registration for participants and admins.
- **Quiz Creation**: Admins can create, edit, and delete quizzes.
- **Attempt Quiz**: User and admin can attempt quiz in decided time window. Quiz also has timer feature.
- **Leaderboard**: Tracks users' performance and ranks them based on their scores.
- **Real-time Analytics**: Graphs and charts displaying user performance and completion rates.
- **Search Functionality**: Users can search for quizzes by name or chapter.
- **Responsive Design**: Optimized UI for both desktop and mobile devices.

## Technologies Used
- **Frontend**: HTML, CSS, JavaScript (Chart.js for data visualization)
- **Backend**: Flask (Python)
- **Database**: SQLite
- **Templating Engine**: Jinja2

## Installation
1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/quiz-master-project.git
   cd quiz-master
   ```
2. **Create and Activate Virtual Environment**
   ```bash
   python -m venv myenv
   source myenv/bin/activate  # On macOS/Linux
   myenv\Scripts\activate  # On Windows
   ```
3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Environment Variables**
   Create a `.env` file and add:
   ```
   SECRET_KEY= <string: your-secret-key>
   SQLALCHEMY_DATABASE_URI= <database-uri>
   admin_username= <string: admin-username>
   admin_password= <string: admin-password>
   admin_fullname="Quiz Master"
   admin_qualification= <strin:admin-qualification>
   ```
5. **Create database**
   ```bash
   flask --app run.py db-create
   ```

6. **Run the Application**
   ```bash
   python run.py
   ```
7. **Access the App**
   Open `http://127.0.0.1:5000` in your browser.

## Usage
### Admin Panel
- Admins can log in and manage quizzes, subjects, chapters, questions, and users.
- View user performance via interactive graphs and leaderboard rankings.
- Search for quizzes, chapters, and subjects using the search bar.

### User Panel
- Users can register, log-in, attempt quizzes, and view their performance.
- Their scores are recorded and displayed on the leaderboard.
- User can also view all scores at `/results/<int:user_id>`
- User Dashboard- `/dashboard`
- Select Quizzes- `/quiz/`

## Database Schema
- **Chapter** (id, name, description, subject_id)
- **Question** (id, question_statement, option1, option2, option3, option4, correct_option, quiz_id)
- **Quiz** (id, name, date_of_quiz, time_duration, chapter_id)
- **Users** (id, fullname, username, password)
- **Score** (id, user_id, quiz_id, total_scored)
- **Subject** (id, name, description)
The ER diagram can be seen in the `/app/photos/ER Diagram.png`



---
**Developed with ❤️ by Surendra Prajapat (22F1001907)**

