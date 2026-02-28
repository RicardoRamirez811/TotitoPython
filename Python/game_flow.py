# Importa el estado global del juego (J) y la clase para guardar historial de rondas
from state import J, RegistroHistorial

# Función utilitaria para obtener elementos del DOM por id
from dom_utils import el

# Reglas del juego: detectar ganador o empate
from rules import obtener_info_ganador, es_empate

# Funciones de render (actualizan la interfaz) y de estado visual (mensaje/insignia)
from ui_render import fijar_estado, renderizar_todo

# IA: función que intenta jugar si el turno es de la CPU
from ai import intentar_jugada_cpu


# ==========================================================
# Lee la configuración desde la UI y la guarda en el estado J
# ==========================================================
def aplicar_config_desde_ui():
    # Lee modo (unica o mejorDe3), rival (jugador o cpu) y dificultad
    J.modo = el("selectModo").value
    J.rival = el("selectRival").value
    J.dificultad = el("selectDificultad").value

    # Define cuántas victorias se necesitan para ganar la serie
    # mejorDe3 => 2 victorias, partida única => 1 victoria
    J.victorias_necesarias = 2 if J.modo == "mejorDe3" else 1

    # Nombres de jugadores desde inputs (si está vacío, usa default)
    nombre_x = (el("inputNombreX").value or "Jugador 1").strip()

    # Si el rival es CPU, por defecto el jugador O se llama CPU
    nombre_o_def = "CPU" if J.rival == "cpu" else "Jugador 2"
    nombre_o = (el("inputNombreO").value or nombre_o_def).strip()

    # Guarda nombres en el estado
    J.jugadores["X"].nombre = nombre_x
    J.jugadores["O"].nombre = nombre_o

    # X nunca es CPU, O sí si rival == cpu
    J.jugadores["X"].es_cpu = False
    J.jugadores["O"].es_cpu = (J.rival == "cpu")


# ==========================================================
# Reinicia TODO lo relacionado a una serie completa
# (marcador, ronda, tablero, historial, flags)
# ==========================================================
def reiniciar_estado_serie():
    J.victorias = {"X": 0, "O": 0}   # Reinicia marcador
    J.ronda = 0                      # Reinicia conteo de rondas
    J.tablero = [""] * 9             # Tablero vacío
    J.turno = "X"                    # Turno inicia en X
    J.linea_ganadora = None          # Sin línea ganadora
    J.historial = []                 # Historial vacío
    J.bloqueado = False              # No bloquea clicks/jugadas
    J.iniciado = False               # Aún no iniciado
    J.serie_finalizada = False       # Serie no terminada


# ==========================================================
# Inicia el juego:
# aplica config, reinicia serie, activa bandera y arranca ronda 1
# ==========================================================
def iniciar_juego():
    aplicar_config_desde_ui()
    reiniciar_estado_serie()
    J.iniciado = True
    iniciar_nueva_ronda()


# ==========================================================
# Inicia una nueva ronda:
# - limpia tablero
# - alterna quién empieza según número de ronda
# - renderiza UI
# - si es turno CPU, intenta su jugada
# ==========================================================
def iniciar_nueva_ronda():
    # Si ya terminó la serie, no se inicia otra ronda
    if J.serie_finalizada:
        fijar_estado(
            "La serie ya terminó. Presiona “Nueva serie” para volver a jugar.",
            "secondary",
            "Serie finalizada"
        )
        renderizar_todo()
        return

    # Incrementa número de ronda
    J.ronda += 1

    # Limpia tablero y línea ganadora
    J.tablero = [""] * 9
    J.linea_ganadora = None

    # Alterna quién inicia:
    # ronda impar -> X, ronda par -> O
    J.turno = "X" if (J.ronda % 2 == 1) else "O"

    # Desbloquea para permitir jugar
    J.bloqueado = False

    # Mensaje de UI
    nombre = J.jugadores[J.turno].nombre
    fijar_estado(
        f"Ronda {J.ronda} iniciada. Turno de {nombre} ({J.turno}).",
        "info",
        "Ronda activa"
    )

    # Renderiza todo (tablero + marcador + estado + historial)
    renderizar_todo()

    # Si el turno inicial es CPU, hace jugada automática
    intentar_jugada_cpu(jugar_en)


# ==========================================================
# Cambia el turno X <-> O
# ==========================================================
def alternar_turno():
    J.turno = "O" if J.turno == "X" else "X"


# ==========================================================
# Finaliza una ronda:
# - bloquea el tablero
# - actualiza marcador si hay ganador
# - agrega al historial
# - renderiza
# - verifica si la serie ya terminó
# ==========================================================
def finalizar_ronda(resultado: str, razon: str):
    # Bloquea jugadas mientras ya terminó la ronda
    J.bloqueado = True

    # Si hay ganador, suma victoria y muestra mensaje
    if resultado in ("X", "O"):
        J.victorias[resultado] += 1
        nombre = J.jugadores[resultado].nombre
        fijar_estado(f"{nombre} ({resultado}) {razon}", "warning", "Ronda finalizada")
    else:
        # Si no hay ganador (empate)
        fijar_estado(f"Empate: {razon}", "warning", "Ronda finalizada")

    # Guarda en historial esta ronda
    J.historial.append(RegistroHistorial(J.ronda, resultado, razon))

    # Renderiza todo para reflejar cambios
    renderizar_todo()

    # Si alguien ya alcanzó las victorias necesarias, termina serie
    if (
        J.victorias["X"] >= J.victorias_necesarias
        or J.victorias["O"] >= J.victorias_necesarias
    ):
        finalizar_serie()


# ==========================================================
# Finaliza la serie completa:
# muestra ganador de serie, bloquea y activa overlay
# ==========================================================
def finalizar_serie():
    # Determina ganador según el marcador
    ganador = "X" if J.victorias["X"] > J.victorias["O"] else "O"
    nombre = J.jugadores[ganador].nombre

    # Mensaje final de serie
    fijar_estado(
        f"¡Serie terminada! Ganador: {nombre} ({ganador}) — "
        f"Marcador {J.victorias['X']}-{J.victorias['O']}.",
        "dark",
        "Serie finalizada"
    )

    # Bloquea interacciones y marca como terminada
    J.bloqueado = True
    J.serie_finalizada = True

    # Renderiza para mostrar overlay y bloquear controles
    renderizar_todo()


# ==========================================================
# Ejecuta una jugada en el tablero (casilla índice)
# ==========================================================
def jugar_en(indice: int):
    # Validaciones: si no se puede jugar, salir
    if J.serie_finalizada or J.bloqueado or not J.iniciado:
        return

    # Si la casilla ya está ocupada, salir
    if J.tablero[indice] != "":
        return

    # Coloca la ficha del jugador actual en el tablero
    J.tablero[indice] = J.turno

    # Verifica si con esa jugada hay ganador
    info = obtener_info_ganador(J.tablero)
    if info:
        ganador, linea = info
        J.linea_ganadora = linea  # Guarda qué línea ganó (para pintar casillas)
        finalizar_ronda(ganador, "ganó por línea de 3.")
        return

    # Verifica empate (tablero lleno)
    if es_empate(J.tablero):
        finalizar_ronda("empate", "la ronda terminó en empate.")
        return

    # Si no terminó, cambia turno y sigue el juego
    alternar_turno()
    renderizar_todo()

    # Si ahora el turno es CPU, que juegue
    intentar_jugada_cpu(jugar_en)


# ==========================================================
# Click del usuario en una casilla
# ==========================================================
def manejar_click_casilla(indice: int):
    # Si no está iniciado o está bloqueado o terminó la serie, ignora
    if not J.iniciado or J.bloqueado or J.serie_finalizada:
        return

    # Si el turno es CPU, el usuario no puede jugar
    if J.jugadores[J.turno].es_cpu:
        return

    # Si es turno humano, realiza la jugada
    jugar_en(indice)


# ==========================================================
# Reinicia SOLO la ronda actual (sin reiniciar marcador)
# ==========================================================
def reiniciar_ronda():
    if not J.iniciado:
        return

    # Si ya terminó serie, no se puede reiniciar ronda
    if J.serie_finalizada:
        fijar_estado(
            "La serie ya terminó. Presiona “Nueva serie” para volver a jugar.",
            "secondary",
            "Serie finalizada"
        )
        renderizar_todo()
        return

    # Si está permitido, inicia nueva ronda (limpia tablero y avanza ronda)
    iniciar_nueva_ronda()


# ==========================================================
# Reinicia la serie completa (marcador e historial a 0)
# Mantiene la config actual (modo, rival, dificultad, nombres)
# ==========================================================
def nueva_serie():
    if not J.iniciado:
        return

    # Aplica configuración actual (por si cambió inputs)
    aplicar_config_desde_ui()

    # Reinicia solo datos de serie, sin apagar el juego
    J.victorias = {"X": 0, "O": 0}
    J.ronda = 0
    J.historial = []
    J.serie_finalizada = False
    J.bloqueado = False

    # Empieza la ronda 1
    iniciar_nueva_ronda()


# ==========================================================
# Rendirse:
# el jugador actual pierde la ronda y gana el otro
# ==========================================================
def rendirse_turno_actual():
    if not J.iniciado or J.bloqueado or J.serie_finalizada:
        return

    # El jugador del turno actual es el perdedor
    perdedor = J.turno
    ganador = "O" if perdedor == "X" else "X"

    # No hay línea ganadora, porque no se ganó por tablero
    J.linea_ganadora = None

    # Finaliza la ronda declarando ganador al rival
    finalizar_ronda(ganador, "ganó porque el rival se rindió.")