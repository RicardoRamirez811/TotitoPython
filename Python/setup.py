from js import document

from state import J
from dom_utils import el, texto
from proxies import guardar_proxy
from ui_render import renderizar_todo
from confirm import pedir_confirmacion, ocultar_confirmacion
from game_flow import (
    iniciar_juego, reiniciar_ronda, nueva_serie,
    rendirse_turno_actual, manejar_click_casilla
)

def construir_tablero():
    cont = el("tablero")
    cont.innerHTML = ""
    for i in range(9):
        col = document.createElement("div")
        col.className = "col-4"

        btn = document.createElement("button")
        btn.className = "btn btn-outline-dark w-100"
        btn.style.height = "90px"
        btn.style.fontSize = "2rem"
        btn.dataset.indice = str(i)
        btn.disabled = True
        btn.textContent = ""

        def handler(evt, indice=i):
            manejar_click_casilla(indice)

        btn.addEventListener("click", guardar_proxy(handler))

        col.appendChild(btn)
        cont.appendChild(col)

def enlazar_eventos():
    def on_cambio_rival(evt):
        es_cpu = (el("selectRival").value == "cpu")
        el("selectDificultad").disabled = (not es_cpu)
        if es_cpu:
            if (el("inputNombreO").value.strip() == "" or el("inputNombreO").value.strip() == "Jugador 2"):
                el("inputNombreO").value = "CPU"
            texto("textoAyudaO", "En CPU, el Jugador 2 se controla automáticamente.")
        else:
            texto("textoAyudaO", "En CPU, este será el nombre de la máquina.")
        renderizar_todo()

    el("selectRival").addEventListener("change", guardar_proxy(on_cambio_rival))

    def on_iniciar(evt):
        pedir_confirmacion(
            "¿Confirmas iniciar el juego? (Reinicia marcador, tablero e historial)",
            lambda: (ocultar_confirmacion(), iniciar_juego())
        )

    el("btnIniciar").addEventListener("click", guardar_proxy(on_iniciar))

    def on_reiniciar(evt):
        pedir_confirmacion(
            "¿Reiniciar la ronda? (Limpia tablero y pasa a nueva ronda)",
            lambda: (ocultar_confirmacion(), reiniciar_ronda())
        )
    el("btnReiniciarRonda").addEventListener("click", guardar_proxy(on_reiniciar))

    def on_nueva_serie(evt):
        pedir_confirmacion(
            "¿Iniciar una nueva serie? (Marcador e historial vuelven a 0)",
            lambda: (ocultar_confirmacion(), nueva_serie())
        )

    el("btnNuevaSerie").addEventListener("click", guardar_proxy(on_nueva_serie))
    el("btnOverlayNuevaSerie").addEventListener("click", guardar_proxy(on_nueva_serie))

    def on_rendirse(evt):
        if not J.iniciado or J.bloqueado or J.serie_finalizada:
            return
        nombre = J.jugadores[J.turno].nombre
        pedir_confirmacion(
            f"¿{nombre} ({J.turno}) se rinde? (Perderá la ronda)",
            lambda: (ocultar_confirmacion(), rendirse_turno_actual())
        )
    el("btnRendirse").addEventListener("click", guardar_proxy(on_rendirse))

    def on_confirmar_si(evt):
        if J.accion_pendiente:
            J.accion_pendiente()
    el("btnConfirmarSi").addEventListener("click", guardar_proxy(on_confirmar_si))

    def on_confirmar_no(evt):
        ocultar_confirmacion()
    el("btnConfirmarNo").addEventListener("click", guardar_proxy(on_confirmar_no))