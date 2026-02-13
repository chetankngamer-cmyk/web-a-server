import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_NAME = "database.db"

# ---------- Initialize Database ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- Home Page (NO TEMPLATE = NO BLANK PAGE) ----------
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")

        if name and email:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email)
            )
            conn.commit()
            conn.close()

    # Fetch users
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    # Build HTML dynamically (prevents blank screen)
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
        <title>Web A Server Dashboard</title>
        <style>
            body {{
                font-family: Arial;
                background-color: #0f172a;
                color: white;
                padding: 40px;
            }}
            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 12px;
                margin-top: 20px;
            }}
            input, button {{
                padding: 10px;
                margin: 5px;
                border-radius: 6px;
                border: none;
            }}
            button {{
                background-color: #38bdf8;
                cursor: pointer;
            }}
            table {{
                width: 100%;
                margin-top: 20px;
                border-collapse: collapse;
            }}
            th, td {{
                padding: 10px;
                border: 1px solid #334155;
            }}
            a {{
                color: #38bdf8;
                font-size: 18px;
            }}
        </style>
    </head>
    <body>

        <h1>🌐 Web A Server Dashboard</h1>
        <p>Server is running successfully </p>

        <div class="card">
            <h2>➕ Add User Data</h2>
            <form method="POST">
                <input type="text" name="name" placeholder="Enter Name" required>
                <input type="email" name="email" placeholder="Enter Email" required>
                <button type="submit">Save Data</button>
            </form>
        </div>

        <div class="card">
            <h2>📊 Stored Database Data</h2>
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
            <h2>📡 API Endpoint</h2>
            <a href="/get_users">Click to View JSON Data</a>
        </div>

    </body>
    </html>
    """

# ---------- API for Web B ----------
@app.route("/get_users", methods=["GET"])
def get_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    conn.close()

    users_list = []
    for row in rows:
        users_list.append({
            "id": row[0],
            "name": row[1],
            "email": row[2]
        })

    return jsonify(users_list)

# ---------- Status Check ----------
@app.route("/status")
def status():
    return {"server": "running", "database": "connected"}

# ---------- Run Server ----------
if __name__ == "__main__":
    app.run()


