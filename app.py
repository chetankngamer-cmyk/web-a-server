import os
import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)

# Use a safe writable path for Render
DB_NAME = os.path.join(os.getcwd(), "database.db")

def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
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

# FAST homepage (no blocking HTML, no DB heavy load)
@app.route("/")
def home():
    return {
        "status": "Web A Server Running",
        "api": "/get_users",
        "message": "Permanent Render API Active"
    }

# Core API for Web B (Client EXE)
@app.route("/get_users")
def get_users():
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        conn.close()

        users = []
        for row in rows:
            users.append({
                "id": row[0],
                "name": row[1],
                "email": row[2]
            })

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)})

# Health route (important for Render)
@app.route("/status")
def status():
    return {"server": "running"}

# REQUIRED for Render dynamic port binding
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
