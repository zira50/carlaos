from core.database import get_connection

def get_events_for_day(date):

    conn = get_connection()
    c = conn.cursor()

    events = []


    # 🧠 TAREAS
    c.execute("""
        SELECT title, tnp_type FROM tasks WHERE scheduled_date=?
    """, (date,))

    for r in c.fetchall():

        icon = "📌"

        if r["tnp_type"] == "full":
            icon = "🏠"
        elif r["tnp_type"] == "morning":
            icon = "☀️"
        elif r["tnp_type"] == "afternoon":
            icon = "🌙"

        events.append({
            "title": f"{icon} {r['title']}"
        })

    # 📅 CITAS
    c.execute("""
        SELECT title FROM appointments WHERE date=?
    """, (date,))
    for r in c.fetchall():
        events.append({"title": "📅 " + r["title"]})

    # 🎂 CUMPLEAÑOS
    c.execute("""
        SELECT name FROM birthdays 
        WHERE strftime('%m-%d', date)=strftime('%m-%d', ?)
    """, (date,))
    for r in c.fetchall():
        events.append({"title": "🎂 " + r["name"]})

    conn.close()
    return events