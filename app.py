from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
from database import init_db, get_db, count_rows

app = Flask(__name__)
app.secret_key = "CHANGE-THIS-SECRET-KEY-BEFORE-DEPLOYMENT"
init_db()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("اسم المستخدم أو كلمة المرور غير صحيحة")
    return render_template("login.html")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/dashboard")
@login_required
def dashboard():
    counts = {t: count_rows(t) for t in
              ["students", "teachers", "departments", "courses", "enrollments", "grades"]}
    return render_template("dashboard.html", counts=counts)

def list_page(table, title, columns):
    with get_db() as db:
        rows = db.execute(f"SELECT * FROM {table} ORDER BY id DESC").fetchall()
    return render_template("table.html", title=title, columns=columns, rows=rows)

@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    if request.method == "POST":
        with get_db() as db:
            db.execute("INSERT INTO students(student_no,name,email,department) VALUES(?,?,?,?)",
                       (request.form["student_no"], request.form["name"],
                        request.form.get("email",""), request.form.get("department","")))
        return redirect(url_for("students"))
    return list_page("students", "إدارة الطلاب",
                     [("student_no","الرقم الجامعي"),("name","اسم الطالب"),
                      ("email","البريد الإلكتروني"),("department","القسم")])

@app.route("/teachers", methods=["GET", "POST"])
@login_required
def teachers():
    if request.method == "POST":
        with get_db() as db:
            db.execute("INSERT INTO teachers(name,email,department) VALUES(?,?,?)",
                       (request.form["name"], request.form.get("email",""),
                        request.form.get("department","")))
        return redirect(url_for("teachers"))
    return list_page("teachers", "إدارة المدرسين",
                     [("name","الاسم"),("email","البريد الإلكتروني"),("department","القسم")])

@app.route("/departments", methods=["GET", "POST"])
@login_required
def departments():
    if request.method == "POST":
        with get_db() as db:
            db.execute("INSERT INTO departments(name) VALUES(?)", (request.form["name"],))
        return redirect(url_for("departments"))
    return list_page("departments", "إدارة الأقسام", [("name","اسم القسم")])

@app.route("/courses", methods=["GET", "POST"])
@login_required
def courses():
    if request.method == "POST":
        with get_db() as db:
            db.execute("INSERT INTO courses(code,name,department) VALUES(?,?,?)",
                       (request.form["code"], request.form["name"],
                        request.form.get("department","")))
        return redirect(url_for("courses"))
    return list_page("courses", "إدارة المقررات",
                     [("code","رمز المقرر"),("name","اسم المقرر"),("department","القسم")])

@app.route("/enrollments", methods=["GET", "POST"])
@login_required
def enrollments():
    if request.method == "POST":
        with get_db() as db:
            db.execute("INSERT INTO enrollments(student_id,course_id) VALUES(?,?)",
                       (request.form["student_id"], request.form["course_id"]))
        return redirect(url_for("enrollments"))
    with get_db() as db:
        students = db.execute("SELECT id, student_no, name FROM students").fetchall()
        courses = db.execute("SELECT id, code, name FROM courses").fetchall()
        rows = db.execute("""SELECT e.id, s.name AS student, c.name AS course
            FROM enrollments e JOIN students s ON s.id=e.student_id
            JOIN courses c ON c.id=e.course_id ORDER BY e.id DESC""").fetchall()
    return render_template("enrollments.html", students=students, courses=courses, rows=rows)

@app.route("/grades", methods=["GET", "POST"])
@login_required
def grades():
    if request.method == "POST":
        with get_db() as db:
            db.execute("INSERT INTO grades(student_id,course_id,grade) VALUES(?,?,?)",
                       (request.form["student_id"], request.form["course_id"], request.form["grade"]))
        return redirect(url_for("grades"))
    with get_db() as db:
        students = db.execute("SELECT id, student_no, name FROM students").fetchall()
        courses = db.execute("SELECT id, code, name FROM courses").fetchall()
        rows = db.execute("""SELECT g.id, s.name AS student, c.name AS course, g.grade
            FROM grades g JOIN students s ON s.id=g.student_id
            JOIN courses c ON c.id=g.course_id ORDER BY g.id DESC""").fetchall()
    return render_template("grades.html", students=students, courses=courses, rows=rows)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
