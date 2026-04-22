from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from core.database import get_connection
from datetime import datetime, date
from core.services.agenda_service import save_cita, save_cumple, save_tnp
from flask import redirect, url_for

import time
import json
import os
import calendar

agenda_bp = Blueprint("agenda", __name__, url_prefix="")

calendar.setfirstweekday(calendar.MONDAY)

today_str = date.today().strftime("%Y-%m-%d")


# =========================================================
# 📅 INICIO / AGENDA
# =========================================================
@agenda_bp.route("/", methods=["GET", "POST"])
@agenda_bp.route("/inicio", methods=["GET", "POST"])
def inicio():

    conn = get_connection()
    c = conn.cursor()

    # =========================================
    # AGENDA
    # =========================================
    from flask import jsonify

    if request.method == "POST":
        from core.services.agenda_service import save_event

        result = save_event(request.form)

        return jsonify(result)

    # -------------------------
    # 📅 CALENDARIO
    # -------------------------
    today = datetime.now()
    today_month = today.month
    today_year = today.year

    month = request.args.get("month", type=int) or today.month
    year = request.args.get("year", type=int) or today.year

    cal = calendar.monthcalendar(year, month)

    prev_month = month - 1 if month > 1 else 12
    next_month = month + 1 if month < 12 else 1
    prev_year = year - 1 if month == 1 else year
    next_year = year + 1 if month == 12 else year

    month_name = calendar.month_name[month].capitalize()

    c.execute("SELECT * FROM events")
    rows = c.fetchall()

    events = {}
    for r in rows:
        date_key = r["date"]

        try:
            date_key = datetime.strptime(date_key, "%Y-%m-%d").strftime("%Y-%m-%d")
        except:
            pass

        events.setdefault(date_key, []).append(r)

    # 🔥 AQUÍ VA
    holiday_events = load_holidays()

    for date, evs in holiday_events.items():
        events.setdefault(date, []).extend(evs)

    conn.close()

    return render_template(
        "inicio.html",
        cal=cal,
        events=events,
        month=month,
        year=year,
        month_name=month_name,
        prev_month=prev_month,
        next_month=next_month,
        prev_year=prev_year,
        next_year=next_year,
        today_str=today_str,
        time=time,
        today_month=today_month,
        today_year=today_year,
    )


# =========================================================
# 🗑 BORRAR
# =========================================================
@agenda_bp.route("/delete_event", methods=["POST"])
def delete_event():
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM events WHERE id=?", (request.form["id"],))

    conn.commit()
    conn.close()

    return redirect(url_for("movimientos.movimientos"))


# =========================================================
# ✏️ EDITAR
# =========================================================
@agenda_bp.route("/edit_event", methods=["POST"])
def edit_event():
    conn = get_connection()
    c = conn.cursor()

    c.execute("UPDATE events SET title=? WHERE id=?",
              (request.form.get("title"), request.form.get("id")))

    conn.commit()
    conn.close()

    return redirect(request.referrer or url_for("movimientos.movimientos"))


# =========================================================
# 🔍 GET EVENTS
# =========================================================
@agenda_bp.route("/get_events")
def get_events():
    date_val = request.args.get("date")

    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM events WHERE date=?", (date_val,))
    rows = c.fetchall()

    conn.close()

    return jsonify([dict(r) for r in rows])


def load_holidays():
    import json
    import os

    path = os.path.join("data", "holidays_2026.json")

    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    holidays = {}
    for h in data:
        holidays.setdefault(h["date"], []).append({
            "type": "holiday",
            "title": h["name"]
        })

    return holidays