import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_NAME = "database.db"

# ---------- Initialize Database ----------
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Home Route (Fast Response) ----------
@app.route("/", methods=["GET"])
def home():
    return """
    <h1>🌐 Web A Server is Running on Render</h1>
    <p>API Endpoint: <a href='/get_users'>/get_users</a></p>
    <p>Status: Active & Connected</p>
    """

# ---------- Add Data API ----------
@app.route("/add_user", methods=["POST"])
def add_user():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

    return {"message": "User added successfully"}

# ---------- Get Users API (Used by Web B) ----------
@app.route("/get_users", methods=["GET"])
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    users = []
    for row in rows:
        users.append({
            "id": row["id"],
            "name": row["name"],
            "email": row["email"]
        })

    return jsonify(users)

# ---------- Health Check (Render uses this) ----------
@app.route("/status")
def status():
    return {"status": "running"}

# IMPORTANT: Do NOT use fixed port for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
