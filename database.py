import sqlite3
from pathlib import Path
from werkzeug.security import generate_password_hash

DB_PATH = Path(__file__).with_name("university.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_no TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT
        );
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            department TEXT
        );
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            department TEXT
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(id),
            course_id INTEGER NOT NULL REFERENCES courses(id)
        );
        CREATE TABLE IF NOT EXISTS grades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL REFERENCES students(id),
            course_id INTEGER NOT NULL REFERENCES courses(id),
            grade REAL NOT NULL
        );
        """)
        defaults = [
            ("admin", "admin123", "admin"),
            ("staff", "staff123", "staff"),
            ("teacher", "teacher123", "teacher"),
        ]
        for username, password, role in defaults:
            db.execute(
                "INSERT OR IGNORE INTO users(username,password_hash,role) VALUES(?,?,?)",
                (username, generate_password_hash(password), role)
            )

def count_rows(table):
    allowed = {"students", "teachers", "departments", "courses", "enrollments", "grades"}
    if table not in allowed:
        return 0
    with get_db() as db:
        return db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
