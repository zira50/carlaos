from flask import Flask, redirect, url_for, session, request
from core.database import get_connection
from datetime import date
from core.services.backup_service import create_backup
from core.db_state import has_db_changed, reset_db_changed
from core.services.backup_service import create_backup
from core.database import init_db

import calendar
import sys
import os
import webbrowser
import threading
import locale
import atexit

# -------------------------
# CONFIG
# -------------------------
locale.setlocale(locale.LC_TIME, 'Spanish_Spain')
calendar.setfirstweekday(calendar.MONDAY)

# -------------------------
# HELPERS
# -------------------------
def open_browser():
    webbrowser.open("http://127.0.0.1:5000/login?app=1")

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.abspath(".")

# -------------------------
# APP INIT
# -------------------------
base_path = get_base_path()

templates_path = os.path.join(base_path, "templates")
static_path = os.path.join(base_path, "static")

app = Flask(
    __name__,
    template_folder=templates_path,
    static_folder=static_path
)

app.config['SECRET_KEY'] = "carlaos_secret"

init_db()

# -------------------------
# BLUEPRINTS
# -------------------------
from routes.agenda import agenda_bp
from routes.insights import insights_bp
from routes.movimientos import movimientos_bp
from routes.auth import auth_bp
from routes.settings import settings_bp  # 👈 NUEVO

app.register_blueprint(agenda_bp)
app.register_blueprint(insights_bp)
app.register_blueprint(movimientos_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(settings_bp)  # 👈 NUEVO

# =========================================================
# 🔐 LOGIN CONTROL
# =========================================================
@app.before_request
def check_login():

    if request.endpoint is None:
        return

    if request.endpoint and (
        request.endpoint.startswith("auth") or 
        request.endpoint == "static"
    ):
        return

    if not session.get("logged"):
        return redirect(url_for("auth.login"))

# =========================================================
# 🏠 HOME
# =========================================================
@app.route("/")
def home():
    return redirect(url_for("agenda.inicio"))

# =========================================================
# 🧱 INIT DB
# =========================================================
def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        title TEXT,
        time TEXT,
        subtype TEXT,
        value REAL,
        status TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        amount REAL,
        concept TEXT,
        date TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # PIN por defecto
    c.execute("SELECT * FROM config WHERE key='pin'")
    if not c.fetchone():
        c.execute("INSERT INTO config (key, value) VALUES ('pin', '1234')")

    conn.commit()
    conn.close()


# =========================================================
# CREAR BACKUP DE LA BBDD
# =========================================================

import atexit
from core.services.backup_service import create_backup
from core.db_state import has_db_changed, reset_db_changed

def on_exit():
    if has_db_changed():
        print("💾 Cambios detectados, creando backup...")
        try:
            create_backup()
            reset_db_changed()
        except Exception as e:
            print("❌ Error creando backup:", e)
    else:
        print("🧘 Sin cambios, no se crea backup")

atexit.register(on_exit)

# =========================================================
# ▶️ RUN
# =========================================================
if __name__ == "__main__":
    if not os.environ.get("ELECTRON"):
        threading.Timer(1, open_browser).start()

    app.run(debug=False)