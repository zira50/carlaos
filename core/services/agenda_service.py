from core.database import get_connection

# =============================================
# 🔧 HELPER DB
# =============================================

def db():
    conn = get_connection()
    return conn, conn.cursor()


# =============================================
# 📍 CITA
# =============================================

def save_cita(data):
    conn, c = db()

    try:
        if data.get("edit_id"):
            c.execute("""
                UPDATE events
                SET time=?, title=?, subtype=?
                WHERE id=?
            """, (
                data.get("time"),
                data.get("title"),
                data.get("subtype"),
                data.get("edit_id")
            ))
        else:
            c.execute("""
                INSERT INTO events (date, type, time, title, subtype)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data["date"],
                "cita",
                data.get("time"),
                data.get("title"),
                data.get("subtype")
            ))

        conn.commit()
        return {"success": True}

    except Exception as e:
        return {"success": False, "msg": str(e)}

    finally:
        conn.close()


# =============================================
# 🎂 CUMPLEAÑOS
# =============================================

def save_cumple(data):
    conn, c = db()

    try:
        if data.get("edit_id"):
            c.execute(
                "UPDATE events SET title=? WHERE id=?",
                (data.get("title"), data.get("edit_id"))
            )
        else:
            c.execute(
                "INSERT INTO events (date, type, title) VALUES (?, ?, ?)",
                (data["date"], "cumple", data.get("title"))
            )

        conn.commit()
        return {"success": True}

    finally:
        conn.close()


# =============================================
# 🏠 TNP
# =============================================

def save_tnp(data):
    conn, c = db()

    try:
        date_val = data["date"]
        nuevo = data.get("subtype")

        if data.get("edit_id"):
            c.execute(
                "UPDATE events SET subtype=? WHERE id=?",
                (nuevo, data.get("edit_id"))
            )
            conn.commit()
            return {"success": True}

        c.execute("""
            SELECT subtype FROM events 
            WHERE date=? AND type='tnp'
        """, (date_val,))

        existing = [r["subtype"] for r in c.fetchall()]

        if "full" in existing:
            return {"success": False, "msg": "⚠️ Ya existe un TNP completo"}

        if nuevo == "full" and existing:
            return {"success": False, "msg": "⚠️ Ya hay medio día"}

        if nuevo in existing:
            return {"success": False, "msg": "⚠️ Ese TNP ya existe"}

        c.execute(
            "INSERT INTO events (date, type, subtype) VALUES (?, ?, ?)",
            (date_val, "tnp", nuevo)
        )

        conn.commit()
        return {"success": True}

    finally:
        conn.close()


# =============================================
# 🧠 TASK
# =============================================

def save_task(data):
    conn, c = db()

    try:
        if data.get("edit_id"):
            c.execute(
                "UPDATE events SET title=? WHERE id=?",
                (data.get("title"), data.get("edit_id"))
            )
        else:
            c.execute("""
                INSERT INTO events (date, type, title, status)
                VALUES (?, ?, ?, 'pending')
            """, (data["date"], "task", data.get("title")))

        conn.commit()
        return {"success": True}

    finally:
        conn.close()


# =============================================
# 🎉 HOLIDAY (manuales + validación)
# =============================================

def save_holiday(data):
    conn, c = db()

    try:
        nombre = (data.get("title") or "").strip().capitalize()

        if not nombre:
            return {"success": False, "msg": "⚠️ Necesita nombre"}

        if data.get("edit_id"):
            c.execute(
                "UPDATE events SET title=? WHERE id=?",
                (nombre, data.get("edit_id"))
            )
        else:
            # evitar duplicados
            c.execute("""
                SELECT 1 FROM events
                WHERE date=? AND type='holiday' AND LOWER(title)=?
            """, (data["date"], nombre.lower()))

            if c.fetchone():
                return {"success": False, "msg": "⚠️ Ya existe ese festivo"}

            c.execute("""
                INSERT INTO events (date, type, title)
                VALUES (?, ?, ?)
            """, (data["date"], "holiday", nombre))

        conn.commit()
        return {"success": True}

    finally:
        conn.close()


# =============================================
# ⏰ GUARDIA
# =============================================

def save_guardia(data):
    conn, c = db()

    try:
        title = data.get("title") or "Guardia"

        if data.get("edit_id"):
            c.execute(
                "UPDATE events SET title=? WHERE id=?",
                (title, data.get("edit_id"))
            )
        else:
            c.execute(
                "INSERT INTO events (date, type, title) VALUES (?, ?, ?)",
                (data["date"], "guardia", title)
            )

        conn.commit()
        return {"success": True}

    finally:
        conn.close()


# =============================================
# ⚡ EXC (por si lo usas)
# =============================================

def save_exc(data):
    conn, c = db()

    try:
        hours = data.get("hours") or 0

        if data.get("edit_id"):
            c.execute(
                "UPDATE events SET value=? WHERE id=?",
                (hours, data.get("edit_id"))
            )
        else:
            c.execute(
                "INSERT INTO events (date, type, value) VALUES (?, ?, ?)",
                (data["date"], "exc", hours)
            )

        conn.commit()
        return {"success": True}

    finally:
        conn.close()


# =============================================
# 🧠 ROUTER PRINCIPAL
# =============================================

def save_event(data):
    tipo = data.get("tipo")

    handlers = {
        "cita": save_cita,
        "cumple": save_cumple,
        "tnp": save_tnp,
        "task": save_task,
        "holiday": save_holiday,
        "guardia": save_guardia,
        "exc": save_exc
    }

    handler = handlers.get(tipo)

    if not handler:
        return {"success": False, "msg": "Tipo no válido"}

    return handler(data)


# =============================================
# 🔍 UTIL
# =============================================

def is_holiday_or_sunday(date_str):
    from datetime import datetime

    conn, c = db()

    c.execute("""
        SELECT 1 FROM events 
        WHERE date=? AND type='holiday'
    """, (date_str,))

    if c.fetchone():
        conn.close()
        return True

    conn.close()

    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.weekday() == 6