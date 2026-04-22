console.log("AGENDA JS CARGADO");

// =========================================
// 📅 ABRIR POPUP
// =========================================
function openPopup(date) {
    const popup = document.getElementById("popup");
    const overlay = document.getElementById("overlay");

    if (!popup || !overlay) return;

    const d = new Date(date);
    date = d.toISOString().split("T")[0];

    popup.classList.add("show");
    overlay.classList.add("show");

    document.getElementById("popup_date").value = date;

    const fechaBonita = d.toLocaleDateString("es-ES", {
        weekday: "long",
        day: "numeric",
        month: "long"
    });

    document.getElementById("popup_title").innerText = "📅 " + fechaBonita;
    document.getElementById("day_events").innerHTML = "<p>Cargando...</p>";

    loadEvents(date);
    updateForm();
}


// =========================================
// 📡 CARGAR EVENTOS
// =========================================
function loadEvents(date) {
    fetch("/get_events?date=" + date)
        .then(res => res.json())
        .then(data => {

            console.log("EVENTOS:", data);

            let html = "";

            data.forEach(e => {
                let text = "";

                if (e.type === "exc") {
                    let hours = e.value ? parseFloat(e.value) : 0;
                    text = "⚡ EXC (" + hours + "h)";
                }

                else if (e.type === "tnp") {
                    if (e.subtype === "full") text = "🏠 Día completo";
                    else if (e.subtype === "morning") text = "☀️ TNPM";
                    else if (e.subtype === "afternoon") text = "🌙 TNPT";
                    else text = "🏠 TNP";
                }

                else if (e.type === "cita") {
                    text = "🩺 " + (e.title || "Cita");
                }

                else if (e.type === "cumple") {
                    text = "🎂 " + (e.title || "Cumpleaños");
                }

                else if (e.type === "holiday") {
                    text = "🎉 " + (e.title || "Festivo");
                }

                else if (e.type === "task") {
                    text = "🧠 " + (e.title || "Tarea");
                }

                else if (e.type === "guardia") {
                    text = "⏰ Guardia";
                }

                else {
                    text = "📌 " + (e.title || e.type);
                }

                html += `
                    <div class="event-card">
                        <div>${text}</div>

                        <div style="margin-top:5px;">
                            <button onclick="editEvent(${e.id}, '${e.type}')">✏️</button>

                            <form method="POST" action="/delete_event" style="display:inline;">
                                <input type="hidden" name="id" value="${e.id}">
                                <button>🗑</button>
                            </form>
                        </div>
                    </div>
                `;
            });

            document.getElementById("day_events").innerHTML =
                html || "<p>No hay eventos</p>";
        })
        .catch(err => {
            console.error("Error cargando eventos:", err);
            document.getElementById("day_events").innerHTML = "<p>Error cargando eventos</p>";
        });
}


// =========================================
// ❌ CERRAR POPUP
// =========================================
function closePopup() {
    const popup = document.getElementById("popup");
    const overlay = document.getElementById("overlay");

    if (!popup || !overlay) return;

    popup.classList.remove("show");
    overlay.classList.remove("show");
}


// =========================================
// 🔄 ACTUALIZAR FORMULARIO
// =========================================
function updateForm() {
    const tipo = document.getElementById("tipo").value;

    const input = document.getElementById("title_input");
    const hoursInput = document.getElementById("hours_input");
    const timeInput = document.getElementById("time_input");
    const subtype = document.getElementById("subtype");

    input.style.display = "block";
    hoursInput.style.display = "none";
    timeInput.style.display = "none";
    subtype.style.display = "none";

    if (tipo === "exc") {
        input.style.display = "none";
        hoursInput.style.display = "block";
    }

    else if (tipo === "cita") {
        subtype.style.display = "block";
        timeInput.style.display = "block";

        subtype.innerHTML = `
            <option value="medico">🩺 Médico</option>
            <option value="otros">📍 Otros</option>
            <option value="nara">👶 Nara</option>
        `;
    }

    else if (tipo === "tnp") {
        input.style.display = "none";
        subtype.style.display = "block";

        subtype.innerHTML = `
            <option value="full">🏠 Día completo</option>
            <option value="morning">☀️ Mañana</option>
            <option value="afternoon">🌙 Tarde</option>
        `;
    }
}


// =========================================
// ✏️ EDITAR EVENTO
// =========================================
function editEvent(id, type) {
    document.getElementById("tipo").value = type;
    document.getElementById("edit_id").value = id;

    updateForm();
}


// =========================================
// 💬 MENSAJES UX
// =========================================
function showMessage(msg, isError = true) {
    const el = document.getElementById("popup_msg");

    el.innerText = msg;
    el.style.color = isError ? "red" : "green";
    el.style.opacity = "1";

    setTimeout(() => {
        el.style.opacity = "0";
    }, 3000);
}


// =========================================
// 🚀 INIT
// =========================================
document.addEventListener("DOMContentLoaded", function () {

    const overlay = document.getElementById("overlay");
    const form = document.getElementById("eventForm");

    if (overlay) {
        overlay.addEventListener("click", closePopup);
    }

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch("/inicio", {
                method: "POST",
                body: formData
            })
                .then(res => res.json())
                .then(data => {
                    console.log("RESPUESTA:", data);

                    if (!data.ok) {
                        showMessage(data.msg, true);
                    } else {
                        showMessage("✅ Guardado", false);
                        openPopup(document.getElementById("popup_date").value);
                    }
                })
                .catch(err => {
                    console.error("Error guardando:", err);
                    showMessage("Error al guardar", true);
                });
        });
    }
    function toggleFinanzas() {
        const el = document.getElementById("finanzas-content");
        el.style.display = el.style.display === "none" ? "block" : "none";
    }

});