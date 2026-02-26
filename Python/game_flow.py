from state import J, RegistroHistorial
from dom_utils import el
from rules import obtener_info_ganador, es_empate
from ui_render import fijar_estado, renderizar_todo
from ai import intentar_jugada_cpu

def aplicar_config_desde_ui():
    J.modo = el("selectModo").value
    J.rival = el("selectRival").value
    J.dificultad = el("selectDificultad").value
    J.victorias_necesarias = 2 if J.modo == "mejorDe3" else 1

    nombre_x = (el("inputNombreX").value or "Jugador 1").strip()
    nombre_o_def = "CPU" if J.rival == "cpu" else "Jugador 2"
    nombre_o = (el("inputNombreO").value or nombre_o_def).strip()

    J.jugadores["X"].nombre = nombre_x
    J.jugadores["O"].nombre = nombre_o
    J.jugadores["X"].es_cpu = False
    J.jugadores["O"].es_cpu = (J.rival == "cpu")

def reiniciar_estado_serie():
    J.victorias = {"X": 0, "O": 0}
    J.ronda = 0
    J.tablero = [""] * 9
    J.turno = "X"
    J.linea_ganadora = None
    J.historial = []
    J.bloqueado = False
    J.iniciado = False
    J.serie_finalizada = False

def iniciar_juego():
    aplicar_config_desde_ui()
    reiniciar_estado_serie()
    J.iniciado = True
    iniciar_nueva_ronda()

def iniciar_nueva_ronda():
    if J.serie_finalizada:
        fijar_estado("La serie ya terminó. Presiona “Nueva serie” para volver a jugar.", "secondary", "Serie finalizada")
        renderizar_todo()
        return

    J.ronda += 1
    J.tablero = [""] * 9
    J.linea_ganadora = None
    J.turno = "X" if (J.ronda % 2 == 1) else "O"
    J.bloqueado = False

    nombre = J.jugadores[J.turno].nombre
    fijar_estado(f"Ronda {J.ronda} iniciada. Turno de {nombre} ({J.turno}).", "info", "Ronda activa")
    renderizar_todo()
    intentar_jugada_cpu(jugar_en)

def alternar_turno():
    J.turno = "O" if J.turno == "X" else "X"

def finalizar_ronda(resultado: str, razon: str):
    J.bloqueado = True

    if resultado in ("X", "O"):
        J.victorias[resultado] += 1
        nombre = J.jugadores[resultado].nombre
        fijar_estado(f"{nombre} ({resultado}) {razon}", "warning", "Ronda finalizada")
    else:
        fijar_estado(f"Empate: {razon}", "warning", "Ronda finalizada")

    J.historial.append(RegistroHistorial(J.ronda, resultado, razon))
    renderizar_todo()

    if J.victorias["X"] >= J.victorias_necesarias or J.victorias["O"] >= J.victorias_necesarias:
        finalizar_serie()

def finalizar_serie():
    ganador = "X" if J.victorias["X"] > J.victorias["O"] else "O"
    nombre = J.jugadores[ganador].nombre

    fijar_estado(
        f"¡Serie terminada! Ganador: {nombre} ({ganador}) — Marcador {J.victorias['X']}-{J.victorias['O']}.",
        "dark",
        "Serie finalizada"
    )
    J.bloqueado = True
    J.serie_finalizada = True
    renderizar_todo()

def jugar_en(indice: int):
    if J.serie_finalizada or J.bloqueado or not J.iniciado:
        return
    if J.tablero[indice] != "":
        return

    J.tablero[indice] = J.turno

    info = obtener_info_ganador(J.tablero)
    if info:
        ganador, linea = info
        J.linea_ganadora = linea
        finalizar_ronda(ganador, "ganó por línea de 3.")
        return

    if es_empate(J.tablero):
        finalizar_ronda("empate", "la ronda terminó en empate.")
        return

    alternar_turno()
    renderizar_todo()
    intentar_jugada_cpu(jugar_en)

def manejar_click_casilla(indice: int):
    if not J.iniciado or J.bloqueado or J.serie_finalizada:
        return
    if J.jugadores[J.turno].es_cpu:
        return
    jugar_en(indice)

def reiniciar_ronda():
    if not J.iniciado:
        return
    if J.serie_finalizada:
        fijar_estado("La serie ya terminó. Presiona “Nueva serie” para volver a jugar.", "secondary", "Serie finalizada")
        renderizar_todo()
        return
    iniciar_nueva_ronda()

def nueva_serie():
    if not J.iniciado:
        return
    aplicar_config_desde_ui()
    J.victorias = {"X": 0, "O": 0}
    J.ronda = 0
    J.historial = []
    J.serie_finalizada = False
    J.bloqueado = False
    iniciar_nueva_ronda()

def rendirse_turno_actual():
    if not J.iniciado or J.bloqueado or J.serie_finalizada:
        return
    perdedor = J.turno
    ganador = "O" if perdedor == "X" else "X"
    J.linea_ganadora = None
    finalizar_ronda(ganador, "ganó porque el rival se rindió.")