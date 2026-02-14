import os
import sqlite3
from flask import Flask, jsonify, request, redirect

app = Flask(__name__)
DB_NAME = os.path.join(os.getcwd(), "database.db")

# ---------- INIT DB ----------
def init_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------- WEB A DASHBOARD ----------
@app.route("/")
def home():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()

    rows = ""
    for u in users:
        rows += f"""
        <tr>
            <td>{u[0]}</td>
            <td>{u[1]}</td>
            <td>{u[2]}</td>
            <td>
                <button onclick="openEdit('{u[0]}','{u[1]}','{u[2]}')">Edit</button>
            </td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Web A - Live Server Dashboard</title>

        <script>
            let isUserInteracting = false;

            function startSmartRefresh() {{
                setInterval(function () {{
                    if (!isUserInteracting) {{
                        location.reload();
                    }}
                }}, 5000);
            }}

            function pauseRefresh() {{
                isUserInteracting = true;
            }}

            function resumeRefresh() {{
                isUserInteracting = false;
            }}

            function openEdit(id, name, email) {{
                pauseRefresh();
                document.getElementById("edit_id").value = id;
                document.getElementById("edit_name").value = name;
                document.getElementById("edit_email").value = email;
                document.getElementById("popup").style.display = "block";
            }}

            function closePopup() {{
                document.getElementById("popup").style.display = "none";
                resumeRefresh();
            }}

            document.addEventListener("DOMContentLoaded", function () {{
                startSmartRefresh();

                document.querySelectorAll("input").forEach(function(el) {{
                    el.addEventListener("focus", pauseRefresh);
                    el.addEventListener("blur", resumeRefresh);
                    el.addEventListener("keydown", pauseRefresh);
                }});
            }});
        </script>

        <style>
            body {{
                font-family: Arial;
                background: #0f172a;
                color: white;
                text-align: center;
                padding: 30px;
            }}
            table {{
                width: 85%;
                margin: auto;
                border-collapse: collapse;
                background: #1e293b;
            }}
            th, td {{
                padding: 12px;
                border: 1px solid #334155;
            }}
            th {{ background: #334155; }}
            button {{
                padding: 6px 12px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                background: #38bdf8;
                font-weight: bold;
            }}
            input {{
                padding: 8px;
                margin: 5px;
                width: 200px;
            }}
            .card {{
                background: #1e293b;
                padding: 20px;
                border-radius: 12px;
                margin: 20px auto;
                width: 85%;
            }}
            .popup {{
                display: none;
                position: fixed;
                top: 30%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #1e293b;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 20px black;
            }}
        </style>
    </head>
    <body>

        <h1>🌐 Web A - Live Server Dashboard</h1>

        <div class="card">
            <h2>➕ Add New User</h2>
            <form method="POST" action="/add_user">
                <input type="text" name="name" placeholder="Enter Name" required>
                <input type="email" name="email" placeholder="Enter Email" required>
                <br><br>
                <button type="submit">Add User</button>
            </form>
        </div>

        <div class="card">
            <h2>📊 Users (Auto Sync + Smart Refresh)</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Action</th>
                </tr>
                {rows}
            </table>
        </div>

        <div class="popup" id="popup">
            <h2>Edit User (Server)</h2>
            <form method="POST" action="/update_user_form">
                <input type="hidden" name="id" id="edit_id">
                <br>
                <input type="text" name="name" id="edit_name" required>
                <br>
                <input type="email" name="email" id="edit_email" required>
                <br><br>
                <button type="submit">Save Changes</button>
                <button type="button" onclick="closePopup()">Cancel</button>
            </form>
        </div>

    </body>
    </html>
    """

# ---------- ADD USER ----------
@app.route("/add_user", methods=["POST"])
def add_user():
    name = request.form.get("name")
    email = request.form.get("email")
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------- UPDATE FROM WEB A ----------
@app.route("/update_user_form", methods=["POST"])
def update_user_form():
    user_id = request.form.get("id")
    name = request.form.get("name")
    email = request.form.get("email")
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))
    conn.commit()
    conn.close()
    return redirect("/")

# ---------- API FOR WEB B ----------
@app.route("/get_users")
def get_users():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    rows = c.fetchall()
    conn.close()
    return jsonify([{"id": r[0], "name": r[1], "email": r[2]} for r in rows])

@app.route("/update_user", methods=["POST"])
def update_user():
    data = request.get_json()
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    c = conn.cursor()
    c.execute("UPDATE users SET name=?, email=? WHERE id=?",
              (data["name"], data["email"], data["id"]))
    conn.commit()
    conn.close()
    return {"message": "Updated"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
