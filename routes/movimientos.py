from flask import Blueprint, render_template, request, redirect, url_for
from core.database import get_connection

movimientos_bp = Blueprint("movimientos", __name__, url_prefix="")

CATEGORIES = ["Comida", "Gasolina", "Casa", "Suscripciones", "Otros"]

CATEGORY_ICONS = {
    "Comida": "🍔",
    "Gasolina": "⛽",
    "Casa": "🏠",
    "Suscripciones": "🎮",
    "Otros": "📦"
}

@movimientos_bp.route("/movimientos", methods=["GET"])
def movimientos():
    conn = get_connection()
    c = conn.cursor()

    search = request.args.get("search")
    tipo = request.args.get("tipo")

    query = "SELECT * FROM events WHERE type='movimiento'"
    params = []

    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if tipo:
        query += " AND subtype=?"
        params.append(tipo)

    query += " ORDER BY date DESC"

    c.execute(query, params)
    movimientos = c.fetchall()

    categories = [(c, c) for c in CATEGORIES]

    conn.close()

    return render_template(
        "movimientos.html",
        movimientos=movimientos,
        categories=categories,
        search=search,
        tipo=tipo,
        icons=CATEGORY_ICONS
    )


@movimientos_bp.route("/add_movimiento", methods=["POST"])
def add_movimiento():
    conn = get_connection()
    c = conn.cursor()

    tipo = request.form.get("tipo")
    category = request.form.get("category")
    amount = float(request.form["amount"])

    # ✔ lógica correcta
    if tipo == "gasto":
        amount = -abs(amount)

        if category not in CATEGORIES:
            return "Categoría no válida", 400

    else:  # ingreso
        amount = abs(amount)
        category = None  # 👈 ingresos no tienen categoría

    c.execute("""
        INSERT INTO events (date, type, subtype, value, title)
        VALUES (?, 'movimiento', ?, ?, ?)
    """, (
        request.form["date"],
        category,
        amount,
        request.form.get("concept")
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("movimientos.movimientos"))