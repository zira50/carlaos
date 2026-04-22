from core.database import get_connection
from flask import flash

# =============================================
# CITA
# =============================================

def save_cita(data):
    conn = get_connection()
    c = conn.cursor()

    date_val = data["date"]
    edit_id = data.get("edit_id")

    if edit_id:
        c.execute("""
            UPDATE events
            SET time=?, title=?, subtype=?
            WHERE id=?
        """, (
            data.get("time"),
            data.get("title"),
            data.get("subtype"),
            edit_id
        ))
    else:
        c.execute("""
            INSERT INTO events (date, type, time, title, subtype)
            VALUES (?, ?, ?, ?, ?)
        """, (
            date_val,
            "cita",
            data.get("time"),
            data.get("title"),
            data.get("subtype")
        ))

    conn.commit()
    conn.close()

# =============================================
# CUMPLEAÑOS
# =============================================

def save_cumple(data):
    from core.database import get_connection

    conn = get_connection()
    c = conn.cursor()

    date_val = data["date"]
    edit_id = data.get("edit_id")

    if edit_id:
        c.execute(
            "UPDATE events SET title=? WHERE id=?",
            (data.get("title"), edit_id)
        )
    else:
        c.execute(
            "INSERT INTO events (date, type, title) VALUES (?, ?, ?)",
            (date_val, "cumple", data.get("title"))
        )

    conn.commit()
    conn.close()

# =============================================
# GUARDAR TNP
# =============================================

def save_tnp(data):
    from core.database import get_connection

    conn = get_connection()
    c = conn.cursor()

    date_val = data["date"]
    edit_id = data.get("edit_id")
    nuevo = data.get("subtype")

    if edit_id:
        c.execute(
            "UPDATE events SET subtype=? WHERE id=?",
            (nuevo, edit_id)
        )
    else:
        # =========================================
        # 🔒 VALIDACIÓN TNP
        # =========================================
        
        c.execute("""
            SELECT subtype FROM events 
            WHERE date=? AND type='tnp'
        """, (date_val,))

        existing = [r["subtype"] for r in c.fetchall()]

        if "full" in existing:
            conn.close()
            return {"ok": False, "msg": "⚠️ Ya existe un TNP de día completo ese día"}

        if nuevo == "full" and existing:
            conn.close()
            return {"ok": False, "msg": "⚠️ No puedes añadir día completo si ya hay medio día"}

        if nuevo in existing:
            conn.close()
            return {"ok": False, "msg": "⚠️ Ese TNP ya está añadido"}

        # =========================================
        # 💾 INSERT
        # =========================================
        c.execute(
            "INSERT INTO events (date, type, subtype) VALUES (?, ?, ?)", 
            (date_val, "tnp", nuevo)
        )


        conn.commit()
        conn.close()

        return {"ok": True}

# =========================================
# 💾 GUARDAR EVENTO
# =========================================

def save_event(data):
    tipo = data.get("tipo")

    if tipo == "cita":
        return save_cita(data)

    elif tipo == "cumple":
        return save_cumple(data)

    elif tipo == "tnp":
        return save_tnp(data)

    elif tipo == "exc":
        return save_exc(data)

    elif tipo == "task":
        return save_task(data)
    
    elif tipo == "holiday":
        return save_holiday(data)
    
    elif tipo == "guardia":
        return save_guardia(data)
    

# =========================================
# 💾 GUARDAR TAREA
# =========================================

def save_task(data):
    from core.database import get_connection

    conn = get_connection()
    c = conn.cursor()

    date_val = data["date"]
    edit_id = data.get("edit_id")
    title = data.get("title")

    if edit_id:
        c.execute(
            "UPDATE events SET title=? WHERE id=?",
            (title, edit_id)
        )
    else:
        c.execute("""
            INSERT INTO events (date, type, title, status)
            VALUES (?, ?, ?, 'pending')
        """, (date_val, "task", title))

    conn.commit()
    conn.close()

# =========================================
# 💾 GUARDAR HOLIDAY
# =========================================

def save_holiday(data):
    from core.database import get_connection
    from flask import flash

    conn = get_connection()
    c = conn.cursor()

    date_val = data["date"]
    edit_id = data.get("edit_id")
    nombre = (data.get("title") or "").strip().capitalize()

    if not nombre:
        conn.close()
        return {"ok": False, "msg": "⚠️ El festivo necesita un nombre"}

    if edit_id:
        c.execute(
            "UPDATE events SET title=? WHERE id=?",
            (nombre, edit_id)
        )
    else:
        # ❌ evitar duplicados
        c.execute("""
            SELECT 1 FROM events
            WHERE date=? AND type='holiday' AND LOWER(title)=?
        """, (date_val, nombre))

        if c.fetchone():
            conn.close()
            return {"ok": False, "msg": "⚠️ Ese festivo ya existe ese día"}

        c.execute("""
            INSERT INTO events (date, type, title)
            VALUES (?, ?, ?)
        """, (date_val, "holiday", nombre))

    conn.commit()
    conn.close()

    return {"ok": True, "msg": "✅ Festivo guardado"}

# =========================================
# 💾 GUARDAR GUARDIA
# =========================================

def save_guardia(data):
    from core.database import get_connection

    conn = get_connection()
    c = conn.cursor()

    date_val = data["date"]
    edit_id = data.get("edit_id")
    title = data.get("title") or "Guardia"

    if edit_id:
        c.execute(
            "UPDATE events SET title=? WHERE id=?",
            (title, edit_id)
        )
    else:
        c.execute(
            "INSERT INTO events (date, type, title) VALUES (?, ?, ?)",
            (date_val, "guardia", title)
        )

    conn.commit()
    conn.close()

def is_holiday_or_sunday(date_str):
    from core.database import get_connection
    from datetime import datetime

    conn = get_connection()
    c = conn.cursor()

    # comprobar festivo
    c.execute("""
        SELECT 1 FROM events 
        WHERE date=? AND type='holiday'
    """, (date_str,))

    if c.fetchone():
        conn.close()
        return True

    conn.close()

    # comprobar domingo
    d = datetime.strptime(date_str, "%Y-%m-%d")
    return d.weekday() == 6  # domingo
