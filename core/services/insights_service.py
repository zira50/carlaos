from core.database import get_connection
from datetime import date

def get_finanzas():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT value FROM events WHERE type='movimiento'")
    rows = c.fetchall()

    ingresos = sum(r["value"] for r in rows if r["value"] and r["value"] > 0)
    gastos = sum(r["value"] for r in rows if r["value"] and r["value"] < 0)
    saldo = ingresos + gastos
    
    conn.close()
    
    return ingresos, gastos, saldo

def get_eventos():
    conn = get_connection()
    c = conn.cursor()

    today = date.today().strftime("%Y-%m-%d")

    # 🎂 CUMPLEAÑOS
    c.execute("""
        SELECT * FROM events 
        WHERE date(date) >= date(?) AND type='cumple'
        ORDER BY date 
        LIMIT 5
    """, (today,))
    cumples = [dict(r) for r in c.fetchall()]

    # 🩺 CITAS
    c.execute("""
        SELECT * FROM events 
        WHERE date(date) >= date(?) AND type='cita'
        ORDER BY date 
        LIMIT 5
    """, (today,))
    citas = [dict(r) for r in c.fetchall()]

    # 👶 NARA
    nara_events = [e for e in citas if e.get("subtype") == "nara"]

    conn.close()

    return cumples, citas, nara_events

def get_gastos_categoria():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT subtype, SUM(value) as total
        FROM events
        WHERE type='movimiento' AND value < 0
        GROUP BY subtype
    """)

    gastos_categoria = [dict(r) for r in c.fetchall()]

    if gastos_categoria:
        max_gasto = max(abs(g["total"] or 0) for g in gastos_categoria)
    else:
        max_gasto = 1

    conn.close()

    return gastos_categoria, max_gasto

def get_kpis():
    from core.database import get_connection
    from datetime import date

    conn = get_connection()
    c = conn.cursor()

    # 🧠 TAREAS
    c.execute("SELECT * FROM events WHERE type='task'")
    tasks = [dict(r) for r in c.fetchall()]

    # 🏠 TNP
    c.execute("SELECT subtype FROM events WHERE type='tnp'")
    rows = c.fetchall()

    tnp_used = 0
    for r in rows:
        if r["subtype"] == "full":
            tnp_used += 1
        elif r["subtype"] in ["morning", "afternoon"]:
            tnp_used += 0.5

    tnp_total = 22
    tnp_left = tnp_total - tnp_used

    # 🌴 VACACIONES
    c.execute("SELECT COUNT(*) as total FROM events WHERE type='vacation'")
    vac_used = c.fetchone()["total"]
    vac_total = 22
    vac_left = vac_total - vac_used

    # ⏰ GUARDIAS
    year = date.today().year

    c.execute("""
        SELECT COUNT(*) as total 
        FROM events 
        WHERE type='guardia' 
        AND strftime('%Y', date) = ?
    """, (str(year),))

    guardias = c.fetchone()["total"] or 0

    # ⚡ EXC
    c.execute("SELECT SUM(value) as total FROM events WHERE type='exc'")
    exc_used = c.fetchone()["total"] or 0
    exc_total = 74
    exc_left = exc_total - exc_used

    conn.close()

    return (
        tasks,
        tnp_used, tnp_left,
        vac_used, vac_left,
        guardias,
        exc_used, exc_left
    )
    