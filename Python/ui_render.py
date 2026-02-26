from state import J
from dom_utils import el, texto, set_insignia

def fijar_estado(mensaje: str, color: str, insignia: str):
    texto("textoEstado", mensaje)
    set_insignia("insigniaTurno", color, insignia)

def renderizar_encabezado():
    texto("etiquetaX", f"{J.jugadores['X'].nombre} (X)")
    texto("etiquetaO", f"{J.jugadores['O'].nombre} (O)")

    texto("marcadorX", str(J.victorias["X"]))
    texto("marcadorO", str(J.victorias["O"]))
    texto("etiquetaRonda", str(J.ronda) if J.iniciado else "-")

    if not J.iniciado:
        fijar_estado("Configura y presiona “Iniciar”.", "secondary", "Sin iniciar")
        return
    if J.bloqueado:
        return

    nombre_turno = J.jugadores[J.turno].nombre
    color = "primary" if J.turno == "X" else "success"
    fijar_estado(f"Turno de {nombre_turno} ({J.turno})", color, f"Turno: {J.turno}")

def renderizar_tablero():
    tablero_div = el("tablero")
    botones = tablero_div.querySelectorAll("button[data-indice]")
    for btn in botones:
        idx = int(btn.dataset.indice)
        btn.textContent = J.tablero[idx] if J.tablero[idx] else ""

        deshabilitar = (not J.iniciado) or J.bloqueado or J.serie_finalizada or (J.tablero[idx] != "")
        btn.disabled = deshabilitar

        btn.classList.remove("btn-success", "btn-outline-dark")
        btn.classList.add("btn-outline-dark")

        if J.linea_ganadora and idx in J.linea_ganadora:
            btn.classList.remove("btn-outline-dark")
            btn.classList.add("btn-success")

def renderizar_historial():
    ul = el("listaHistorial")
    ul.innerHTML = ""
    if len(J.historial) == 0:
        from js import document
        li = document.createElement("li")
        li.className = "list-group-item text-muted"
        li.textContent = "Aún no hay rondas registradas."
        ul.appendChild(li)
        return

    from js import document
    for h in reversed(J.historial):
        li = document.createElement("li")
        li.className = "list-group-item"

        if h.resultado == "empate":
            res = "Empate"
        else:
            res = f"Ganó {J.jugadores[h.resultado].nombre} ({h.resultado})"

        li.innerHTML = f"<strong>Ronda {h.ronda}:</strong> {res} <span class='text-muted'>— {h.razon}</span>"
        ul.appendChild(li)

def renderizar_controles():
    activo = J.iniciado

    el("btnReiniciarRonda").disabled = (not activo) or J.serie_finalizada
    el("btnRendirse").disabled = (not activo) or J.serie_finalizada
    el("btnNuevaSerie").disabled = (not activo)

    select_rival = el("selectRival").value
    el("selectDificultad").disabled = (select_rival != "cpu")

def renderizar_overlay():
    overlay = el("overlaySerieFinalizada")
    if J.iniciado and J.serie_finalizada:
        overlay.classList.remove("d-none")
        overlay.classList.add("d-flex")
    else:
        overlay.classList.add("d-none")
        overlay.classList.remove("d-flex")

def renderizar_todo():
    renderizar_tablero()
    renderizar_encabezado()
    renderizar_controles()
    renderizar_historial()
    renderizar_overlay()