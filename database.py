import sqlite3
from contextlib import closing
from pathlib import Path


DB_PATH = Path("ardhanarishwar.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                mode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                mode TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS resume_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_name TEXT,
                score INTEGER,
                analysis TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS interview_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                score INTEGER,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def save_message(conversation_id, role, content):
    try:
        with closing(get_connection()) as conn:
            conn.execute(
                "INSERT INTO messages (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, role, content),
            )
            conn.commit()
    except sqlite3.Error:
        return False
    return True


def create_conversation(title="AI Conversation", mode="General"):
    try:
        with closing(get_connection()) as conn:
            cursor = conn.execute(
                "INSERT INTO conversations (title, mode) VALUES (?, ?)",
                (title, mode),
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error:
        return 1


def save_resume_analysis(file_name, score, analysis):
    try:
        with closing(get_connection()) as conn:
            conn.execute(
                "INSERT INTO resume_analysis (file_name, score, analysis) VALUES (?, ?, ?)",
                (file_name, score, analysis),
            )
            conn.commit()
    except sqlite3.Error:
        return False
    return True


def save_interview_result(role, score, feedback):
    try:
        with closing(get_connection()) as conn:
            conn.execute(
                "INSERT INTO interview_results (role, score, feedback) VALUES (?, ?, ?)",
                (role, score, feedback),
            )
            conn.commit()
    except sqlite3.Error:
        return False
    return True


def get_analytics():
    defaults = {
        "resume_score": 0,
        "interview_score": 0,
        "resume_count": 0,
        "interview_count": 0,
    }
    try:
        with closing(get_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT AVG(score), COUNT(*) FROM resume_analysis")
            resume_avg, resume_count = cursor.fetchone()
            cursor.execute("SELECT AVG(score), COUNT(*) FROM interview_results")
            interview_avg, interview_count = cursor.fetchone()
            return {
                "resume_score": int(resume_avg or 0),
                "interview_score": int(interview_avg or 0),
                "resume_count": resume_count,
                "interview_count": interview_count,
            }
    except sqlite3.Error:
        return defaults
