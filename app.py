from flask import Flask, request, redirect, session, render_template
from playwright.sync_api import sync_playwright
import sqlite3

app = Flask(__name__)
app.secret_key = "secreto123"  # necesario para sesiones

# -----------------------
# DB
# -----------------------
def db():
    return sqlite3.connect("data.db")

def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_total_banco():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=false)

            # usar sesión guardada
            context = browser.new_context(storage_state="estado.json")
            page = context.new_page()

            page.goto("https://portalpersonas.bancochile.cl")

            page.wait_for_timeout(5000)

            elementos = page.locator("text=$").all_text_contents()

            total = 0

            for e in elementos:
                try:
                    limpio = e.replace("$", "").replace(".", "").replace(",", "")
                    monto = int(limpio)
                    total += monto
                except:
                    continue

            browser.close()
            return total

    except Exception as e:
        print("ERROR PLAYWRIGHT:", e)
        return 0

# -----------------------
# HOME (requiere login)
# -----------------------
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")

    return render_template("home.html", user=session["user"])

# -----------------------
# REGISTER
# -----------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO usuarios (username, password) VALUES (?, ?)",
            (user, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# -----------------------
# LOGIN
# -----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        password = request.form["password"]

        conn = db()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM usuarios WHERE username=? AND password=?",
            (user, password)
        )
        result = cur.fetchone()
        conn.close()

        if result:
            session["user"] = user
            return redirect("/")
        else:
            return render_template("login.html", error="Usuario o password incorrecto")

    return render_template("login.html")

# -----------------------
# LOGOUT
# -----------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")




@app.route("/api/total")
def api_total():
    if "user" not in session:
        return {"error": "no autorizado"}, 401

    total = get_total_banco()

    return {"total": total}


# -----------------------
# RUN
# -----------------------
app.run(host="0.0.0.0", port=5000)