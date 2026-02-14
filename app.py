import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import (
    LoginManager, UserMixin,
    login_user, login_required,
    logout_user, current_user
)
import pymysql
from werkzeug.security import check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
# Loading from .env as requested
app.secret_key = os.getenv("SECRET_KEY")

# -----------------------
# LOGIN MANAGER
# -----------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# -----------------------
# DATABASE CONNECTION
# -----------------------
def get_db():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

# -----------------------
# USER CLASS
# -----------------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = str(id)
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    db.close()
    if user:
        return User(id=user['id'], username=user['username'])
    return None

# -----------------------
# ROUTES
# -----------------------

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Matching your HTML name="username" and name="password"
        username = request.form.get('username')
        password = request.form.get('password')

        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        db.close()

        # UPDATED: Using 'password_hash' to match your database column
        if user and check_password_hash(user['password_hash'], password):
            user_obj = User(id=user['id'], username=user['username'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password")

    return render_template('login.html')

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    cur = db.cursor()

    # Get student count
    cur.execute("SELECT COUNT(*) AS total FROM students")
    s_result = cur.fetchone()
    s_count = s_result['total'] if s_result else 0

    # Get class count
    cur.execute("SELECT COUNT(*) AS total FROM tblclass")
    c_result = cur.fetchone()
    c_count = c_result['total'] if c_result else 0

    # UPDATED: Join using studentName and classId to match your schema
    cur.execute("""
        SELECT s.studentName AS name, c.className 
        FROM students s
        LEFT JOIN tblclass c ON s.classId = c.classId
    """)
    students = cur.fetchall()

    cur.close()
    db.close()

    return render_template(
        'index.html',
        students=students,
        s_count=s_count,
        c_count=c_count
    )

@app.route('/manage_classes')
@login_required
def manage_classes():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT * FROM tblclass")
    classes = cur.fetchall()
    db.close()
    return render_template('manage_classes.html', classes=classes)

@app.route('/add_class', methods=['POST'])
@login_required
def add_class():
    name = request.form.get('class_name')
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO tblclass (className) VALUES (%s)", (name,))
    db.commit()
    db.close()
    return redirect(url_for('manage_classes'))

@app.route('/manage_students')
@login_required
def manage_students():
    db = get_db()
    cur = db.cursor()
    # UPDATED: Column names synchronized with database schema
    cur.execute("""
        SELECT s.student_id AS id, s.studentName AS name, c.className
        FROM students s
        LEFT JOIN tblclass c ON s.classId = c.classId
    """)
    students = cur.fetchall()

    cur.execute("SELECT * FROM tblclass")
    classes = cur.fetchall()
    db.close()

    return render_template(
        'manage_students.html',
        students=students,
        classes=classes
    )

@app.route('/add_student', methods=['POST'])
@login_required
def add_student():
    name = request.form.get('name')
    class_id = request.form.get('class_id')
    db = get_db()
    cur = db.cursor()
    # UPDATED: Correct column name studentName
    cur.execute(
        "INSERT INTO students (studentName, classId) VALUES (%s, %s)",
        (name, class_id)
    )
    db.commit()
    db.close()
    return redirect(url_for('manage_students'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == "__main__":
    # Running on 0.0.0.0 for AWS accessibility
    app.run(host="0.0.0.0", port=5000, debug=True)


