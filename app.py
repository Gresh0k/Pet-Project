from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from mcrcon import MCRcon
import re
import sqlite3
from functools import wraps




app = Flask(__name__)

RCON_HOST = "localhost"
RCON_PORT = 25575
RCON_PASSWORD = "89658965"

app.secret_key = "896589658965"

def init_db():
    db = sqlite3.connect("admins.db")
    cur = db.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)
    cur.execute("SELECT * FROM admins WHERE role='owner'")
    owner = cur.fetchone()

    if not owner:
        cur.execute(
            "INSERT INTO admins (username, password, role) VALUES (?, ?, ?)",
            ("1", "11", "owner")
        )

    db.commit()
    db.close()

def get_db():
    return sqlite3.connect("admins.db")


def run_rcon(cmd):
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            return mcr.command(cmd)
    except Exception as e:
        return str(e)

def strip_mc_colors(text: str) -> str:
    return re.sub(r'§.', '', text)

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper

def owner_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("login"))

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT role FROM admins WHERE username=?",
            (session["admin"],)
        )
        role = cur.fetchone()
        db.close()

        if not role or role[0] != "owner":
            return "Доступ запрещён", 403

        return func(*args, **kwargs)
    return wrapper



@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])

def login():
    if "admin" in session:
        return redirect(url_for("index"))
    
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        )
        admin = cur.fetchone()
        db.close()

        if admin:
            session["admin"] = username
            return redirect(url_for("index"))
        else:
            return render_template(
                "login.html",
                error="Неверный логин или пароль"
            )

    return render_template("login.html")

@app.route("/kick")
@login_required
def kick_menu():
    resp = run_rcon("list")
    print(resp)
    players = []
    if ":" in resp:
        players_txt = resp.split(":")[1].strip()
        players = [strip_mc_colors(p.strip()) for p in players_txt.split(",") if p.strip()]
    return render_template("kick.html", players=players)

@app.get("/kick_list")
@login_required
def kick_list():
    resp = run_rcon("list")
    players = []

    if ":" in resp:
        players_txt = resp.split(":")[1].strip()
        players = [strip_mc_colors(p.strip()) for p in players_txt.split(",") if p.strip()]
    return jsonify(players)


@app.post("/kick_player")
@login_required
def kick_player():
    raw_player = request.form["player"]
    player = strip_mc_colors(raw_player)

    reason = request.form["reason"]

    run_rcon(f'kick {player} {reason}')
    return redirect("/")


@app.post("/ban_player")
@login_required
def ban_player():
    raw_player = request.form["player"]
    player = strip_mc_colors(raw_player)

    reason = request.form["reason"]
    duration = request.form["duration"]

    if duration == "permanent":
        run_rcon(f'ban {player} {reason}')
    else:
        run_rcon(f'tempban {player} {duration} {reason}')
    return redirect("/")

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("login"))

@app.route("/admins", methods=["GET", "POST"])
@owner_required
def admins_panel():
    db = get_db()
    cur = db.cursor()

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            cur.execute(
                "INSERT INTO admins (username, password, role) VALUES (?, ?, 'admin')",
                (username, password)
            )
            db.commit()
        except sqlite3.IntegrityError:
            pass

    cur.execute("SELECT id, username, role FROM admins")
    admins = cur.fetchall()
    db.close()

    return render_template("admins.html", admins=admins)

@app.post("/admins/delete/<int:admin_id>")
@owner_required
def delete_admin(admin_id):
    db = get_db()
    cur = db.cursor()
    
    cur.execute("SELECT role FROM admins WHERE id=?", (admin_id,))
    role = cur.fetchone()

    if role and role[0] != "owner":
        cur.execute("DELETE FROM admins WHERE id=?", (admin_id,))
        db.commit()

    db.close()
    return redirect(url_for("admins_panel"))



if __name__ == "__main__":
    init_db()
    app.run(debug=True)
