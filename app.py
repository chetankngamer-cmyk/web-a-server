import os
import sqlite3
from flask import Flask, jsonify, request
import webbrowser
import threading

def open_browser():
    webbrowser.open("http://127.0.0.1:10000")

threading.Timer(2, open_browser).start()


app = Flask(__name__)

# Safe database path (works on Render + local)
DB_NAME = os.path.join(os.getcwd(), "database.db")

# ---------- Initialize Database ----------
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

# ---------- GUI DASHBOARD (Web A Frontend) ----------
@app.route("/", methods=["GET"])
def home():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    table_rows = ""
    for user in users:
        table_rows += f"""
        <tr>
            <td>{user[0]}</td>
            <td>{user[1]}</td>
            <td>{user[2]}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Web A Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background: #0f172a;
                color: white;
                padding: 40px;
                text-align: center;
            }}
            h1 {{
                color: #38bdf8;
            }}
            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 12px;
                margin: 20px auto;
                width: 80%;
                max-width: 800px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                padding: 10px;
                border: 1px solid #334155;
            }}
            th {{
                background: #334155;
            }}
            a {{
                color: #38bdf8;
                font-size: 18px;
                text-decoration: none;
            }}
            input, button {{
                padding: 10px;
                margin: 5px;
                border-radius: 6px;
                border: none;
            }}
            button {{
                background: #38bdf8;
                cursor: pointer;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>

        <h1>🌐 Web A Cloud Dashboard</h1>

        <div class="card">
            <h2>🟢 Server Status: Running</h2>
            <p>Hosted on Render | Permanent API Active</p>
        </div>

        <div class="card">
            <h2>➕ Add New User</h2>
            <form method="POST" action="/add_user">
                <input type="text" name="name" placeholder="Enter Name" required>
                <input type="email" name="email" placeholder="Enter Email" required>
                <br>
                <button type="submit">Save User</button>
            </form>
        </div>

        <div class="card">
            <h2>📊 Stored Users (Database)</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                </tr>
                {table_rows}
            </table>
        </div>

        <div class="card">
            <h2>📡 API Endpoint for Web B</h2>
            <p><a href="/get_users">/get_users (Click to view JSON API)</a></p>
        </div>

    </body>
    </html>
    """

# ---------- ADD USER FROM GUI ----------
@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")

    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()

    return """
    <script>
        window.location.href = "/";
    </script>
    """

# ---------- API FOR WEB B (CLIENT EXE) ----------
@app.route("/get_users", methods=["GET"])
def get_users():
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

# ---------- HEALTH CHECK ----------
@app.route("/status")
def status():
    return {"server": "running", "message": "Web A GUI + API Active"}

# ---------- RENDER + LOCAL COMPATIBLE RUN ----------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
