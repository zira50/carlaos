from flask import Blueprint, render_template
from core.database import get_connection
from datetime import date
from core.services.insights_service import get_eventos, get_finanzas, get_gastos_categoria, get_kpis

insights_bp = Blueprint("insights", __name__)

@insights_bp.route("/insights")
def insights():

    # =========================================================
    # 🔌 CONEXIÓN DB
    # =========================================================
    conn = get_connection()
    c = conn.cursor()

    # =========================================================
    # 📅 EVENTOS (SERVICE)
    # =========================================================
    cumples, citas, nara_events = get_eventos()

    # =========================================================
    # 💸 GASTOS POR CATEGORÍA
    # =========================================================
    gastos_categoria, max_gasto = get_gastos_categoria()

    # =========================================================
    # 💰 FINANZAS
    # =========================================================
    ingresos, gastos, saldo = get_finanzas()

    # =========================================================
    # KPIS - Tareas, Guardias, Vacaciones, Exc
    # =========================================================
    tasks, tnp_used, tnp_left, vac_used, vac_left, guardias, exc_used, exc_left = get_kpis()

    # =========================================================
    # 🔌 CERRAR DB
    # =========================================================
    conn.close()

    # =========================================================
    # 🎨 RENDER
    # =========================================================
    return render_template(
        "insights.html",

        # KPIs
        tnp_used=tnp_used,
        tnp_left=tnp_left,
        vac_used=vac_used,
        vac_left=vac_left,
        guardias=guardias,
        exc_used=exc_used,
        exc_left=exc_left,

        # Finanzas
        saldo=saldo,
        ingresos=ingresos,
        gastos=gastos,
        gastos_categoria=gastos_categoria,
        max_gasto=max_gasto,

        # Tareas
        tasks=tasks,

        # Eventos
        cumples=cumples,
        citas=citas,
        nara_events=nara_events,
    )