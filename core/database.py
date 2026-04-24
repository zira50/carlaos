import sqlite3
import os
import sys

from core.db_state import mark_db_changed

# =========================================================
# 📁 PATH SEGURO (PORTABLE READY)
# =========================================================

def get_base_path():
    if getattr(sys, 'frozen', False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    data_path = os.path.join(base, "data")

    if not os.path.exists(data_path):
        os.makedirs(data_path)

    return data_path


def get_db_path():
    path = os.path.join(get_base_path(), "database.db")
    print("DB PATH:", path)
    return path
    

# Crear DB si no existe
if not os.path.exists(get_db_path()):
    open(get_db_path(), 'w').close()

# =========================================================
# 🔌 CONNECTION
# =========================================================

def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn

# =========================================================
# 🧱 INIT DB (REFORMADO PERO COMPATIBLE)
# =========================================================

def init_db():
    conn = get_connection()
    c = conn.cursor()

    # =====================
    # CONFIG
    # =====================
    c.execute("""
    CREATE TABLE IF NOT EXISTS config (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # =====================
    # EVENTS (TABLA PRINCIPAL)
    # =====================
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        type TEXT,
        title TEXT,
        time TEXT,
        subtype TEXT,
        value REAL
    )
    """)

    # =====================
    # TRANSACTIONS
    # =====================
    c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        amount REAL,
        concept TEXT,
        date TEXT,
        payment_method TEXT,
        category TEXT
    )
    """)

    # =====================
    # TASKS (LO CONSERVAMOS)
    # =====================
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        status TEXT,
        scheduled_date TEXT,
        recurrence TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # =====================
    # PIN POR DEFECTO
    # =====================
    c.execute("SELECT * FROM config WHERE key='pin'")
    if not c.fetchone():
        c.execute("INSERT INTO config (key, value) VALUES ('pin', '1234')")

    conn.commit()
    conn.close()

# =========================================================
# 📅 EVENTS
# =========================================================

def add_event(date, type, title=None, time=None, subtype=None, value=None):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO events (date, type, title, time, subtype, value)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, type, title, time, subtype, value))

    conn.commit()
    conn.close()

    mark_db_changed()


def get_events():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM events ORDER BY date DESC")
    data = c.fetchall()

    conn.close()
    return data

# =========================================================
# 💸 TRANSACTIONS
# =========================================================

def add_transaction(type, amount, concept, date, payment_method=None, category=None):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO transactions (type, amount, concept, date, payment_method, category)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (type, amount, concept, date, payment_method, category))

    conn.commit()
    conn.close()

    mark_db_changed()


def get_transactions():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT *
        FROM transactions
        ORDER BY date DESC
    """)

    data = c.fetchall()
    conn.close()
    return data

# =========================================================
# 🧠 TASKS
# =========================================================

def add_task(title, status="pending", scheduled_date=None):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        INSERT INTO tasks (title, status, scheduled_date)
        VALUES (?, ?, ?)
    """, (title, status, scheduled_date))

    conn.commit()
    conn.close()

    mark_db_changed()


def get_tasks():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM tasks ORDER BY created_at DESC")
    data = c.fetchall()

    conn.close()
    return data