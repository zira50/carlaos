from flask import Blueprint, render_template, request, redirect, url_for, session
from core.database import get_connection
from flask import request
import os
import sys

auth_bp = Blueprint("auth", __name__, url_prefix="")

@auth_bp.route("/shutdown", methods=["POST"])
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')

    if func:
        func()
        return "Servidor apagado"

    # 💣 fallback brutal (por si no existe)
    os._exit(0)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT value FROM config WHERE key='pin'")
    row = c.fetchone()

    error = None
    success = False

    if request.method == "POST":
        if row and request.form.get("pin") == row["value"]:
            session["logged"] = True
            success = True
        else:
            error = "El PIN introducido no es correcto"

    conn.close()

    return render_template(
        "login.html",
        error=error,
        success=success
    )

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))