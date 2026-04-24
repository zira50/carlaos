from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from core.database import get_connection, get_db_path
from core.services.backup_service import create_backup, get_db_file
from datetime import datetime, timedelta
from core.services.agenda_service import is_holiday_or_sunday
import os
import shutil

# =========================================================
# 🔧 BLUEPRINT (SIEMPRE ARRIBA)
# =========================================================
settings_bp = Blueprint("settings", __name__)


# =========================================================
# ⚙️ SETTINGS
# =========================================================
@settings_bp.route("/settings", methods=["GET", "POST"])
def settings_page():
    conn = get_connection()
    c = conn.cursor()

    # -------------------------
    # POST
    # -------------------------
    if request.method == "POST":
        action = request.form.get("action")

        # 🌴 VACACIONES
        if action == "add_vacation":
            start = request.form.get("start")
            end = request.form.get("end")

            if not start or not end:
                flash("⚠️ Debes seleccionar un rango de fechas")
                return redirect(url_for("settings.settings_page"))

            d1 = datetime.strptime(start, "%Y-%m-%d")
            d2 = datetime.strptime(end, "%Y-%m-%d")

            count = 0
            while d1 <= d2:
                date_str = d1.strftime("%Y-%m-%d")

                if not is_holiday_or_sunday(date_str):
                    # 🔍 evitar duplicados
                    c.execute("""
                        SELECT 1 FROM events
                        WHERE date=? AND type='vacation'
                    """, (date_str,))

                    if not c.fetchone():
                        c.execute(
                            "INSERT INTO events (date, type) VALUES (?, 'vacation')",
                            (date_str,)
                        )
                        count += 1

                d1 += timedelta(days=1)

            flash(f"🌴 Vacaciones guardadas ({count} días)")

        conn.commit()
        conn.close()
        return redirect(url_for("settings.settings_page"))

    conn.close()

    # -------------------------
    # 📂 LISTAR BACKUPS
    # -------------------------
    backup_dir = os.path.join(os.path.dirname(get_db_file()), "backups")

    backups = [
        os.path.join(backup_dir, f)
        for f in os.listdir(backup_dir)
        if f.startswith("backup_") and f.endswith(".db")
    ]

    # ordenar por fecha (últimos primero)
    backups.sort(reverse=True)

    return render_template(
        "settings.html",
        hours=0,
        tnp="22",
        backups=backups
    )


# =========================================================
# 🔐 CAMBIAR PIN
# =========================================================
@settings_bp.route("/change_pin", methods=["POST"])
def change_pin():
    conn = get_connection()
    c = conn.cursor()

    current = request.form.get("current_pin")
    new = request.form.get("new_pin")
    confirm = request.form.get("confirm_pin")

    c.execute("SELECT value FROM config WHERE key='pin'")
    row = c.fetchone()

    if not row:
        flash("❌ Error interno")
    elif row["value"] != current:
        flash("❌ PIN actual incorrecto")
    elif new != confirm:
        flash("❌ Los PIN no coinciden")
    else:
        c.execute("UPDATE config SET value=? WHERE key='pin'", (new,))
        conn.commit()
        flash("✅ PIN actualizado")

    conn.close()
    return redirect(url_for("settings.settings_page"))


# =========================================================
# 💾 BACKUP
# =========================================================
@settings_bp.route("/backup", methods=["POST"])
def backup():
    try:
        path = create_backup()
        flash(f"💾 Backup creado: {os.path.basename(path)}")
    except Exception as e:
        flash(f"❌ Error creando backup: {str(e)}")

    return redirect(url_for("settings.settings_page"))


# =========================================================
# 📤 EXPORTAR
# =========================================================
@settings_bp.route("/export")
def export():
    try:
        return send_file(
            get_db_file(),
            as_attachment=True,
            download_name="carlaos_backup.db"
        )
    except Exception as e:
        flash(f"❌ Error exportando: {str(e)}")
        return redirect(url_for("settings.settings_page"))


# =========================================================
# ♻️ RESTAURAR BACKUP
# =========================================================
@settings_bp.route("/restore_backup", methods=["POST"])
def restore_backup():
    backup_file = request.form.get("backup_file")

    if not backup_file or not os.path.exists(backup_file):
        flash("❌ Backup no válido")
        return redirect(url_for("settings.settings_page"))

    try:
        db_path = get_db_path()
        shutil.copy(backup_file, db_path)

        flash("♻️ Backup restaurado correctamente")
    except Exception as e:
        flash(f"❌ Error restaurando: {str(e)}")

    return redirect(url_for("settings.settings_page"))