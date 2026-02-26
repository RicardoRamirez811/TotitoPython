from dataclasses import dataclass
from typing import List, Optional, Tuple, Callable
import random

from js import document, console, setTimeout
from pyodide.ffi import create_proxy

# =========================================================
# Guardar proxies para que Pyodide NO los destruya (FIX)
# =========================================================
PROXIES = []

def guardar_proxy(func):
  p = create_proxy(func)
  PROXIES.append(p)
  return p

# =========================
# Utilidades DOM
# =========================

def el(id_: str):
    return document.getElementById(id_)

def texto(id_: str, valor: str):
    el(id_).textContent = valor

def clases(id_: str):
    return el(id_).classList

def mostrar(id_: str):
    clases(id_).remove("d-none")

def ocultar(id_: str):
    clases(id_).add("d-none")

def set_insignia(id_: str, color: str, contenido: str):
    nodo = el(id_)
    nodo.className = f"badge text-bg-{color}"
    nodo.textContent = contenido

# =========================
# Estado del juego
# =========================

@dataclass
class Jugador:
    nombre: str
    es_cpu: bool = False

@dataclass
class RegistroHistorial:
    ronda: int
    resultado: str  # "X", "O" o "empate"
    razon: str

class EstadoJuego:
    def __init__(self):
        self.modo = "unica"            # unica | mejorDe3
        self.rival = "jugador"         # jugador | cpu
        self.dificultad = "facil"      # facil | medio | dificil
        self.victorias_necesarias = 1

        self.jugadores = {
            "X": Jugador("Jugador 1", False),
            "O": Jugador("Jugador 2", False),
        }

        self.tablero: List[str] = [""] * 9
        self.turno: str = "X"
        self.iniciado: bool = False
        self.bloqueado: bool = False

        self.ronda: int = 0
        self.victorias = {"X": 0, "O": 0}
        self.serie_finalizada: bool = False

        self.linea_ganadora: Optional[List[int]] = None
        self.historial: List[RegistroHistorial] = []

        self.accion_pendiente: Optional[Callable[[], None]] = None

J = EstadoJuego()

console.log("✅ PyScript cargó app.py")
document.body.insertAdjacentHTML("afterbegin", "<div class='alert alert-info m-2'>✅ Python (PyScript) cargado</div>")

# =========================
# Reglas
# =========================

LINEAS = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
]

def obtener_info_ganador(tablero: List[str]) -> Optional[Tuple[str, List[int]]]:
    for linea in LINEAS:
        a,b,c = linea
        if tablero[a] and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a], linea
    return None

def es_empate(tablero: List[str]) -> bool:
    return all(c != "" for c in tablero)

def casillas_vacias(tablero: List[str]) -> List[int]:
    return [i for i, v in enumerate(tablero) if v == ""]

# =========================
# UI Render
# =========================

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
        li = document.createElement("li")
        li.className = "list-group-item text-muted"
        li.textContent = "Aún no hay rondas registradas."
        ul.appendChild(li)
        return

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

    # ✅ Reiniciar ronda debe estar habilitado si el juego está activo y la serie NO ha terminado
    el("btnReiniciarRonda").disabled = (not activo) or J.serie_finalizada

    # ✅ Rendirse igual: solo se bloquea si la serie ya terminó
    el("btnRendirse").disabled = (not activo) or J.serie_finalizada

    # ✅ Nueva serie: habilitado mientras el juego esté iniciado
    el("btnNuevaSerie").disabled = (not activo)

    # dificultad solo si cpu
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

# =========================
# Confirmación
# =========================

def pedir_confirmacion(mensaje: str, accion: Callable[[], None]):
    J.accion_pendiente = accion
    texto("textoConfirmacion", mensaje)
    mostrar("cajaConfirmacion")

def ocultar_confirmacion():
    J.accion_pendiente = None
    ocultar("cajaConfirmacion")

# =========================
# Configuración y flujo
# =========================

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
    intentar_jugada_cpu()

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
    intentar_jugada_cpu()

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

# =========================
# IA (CPU)
# =========================

def cpu_facil() -> Optional[int]:
    vacias = casillas_vacias(J.tablero)
    return random.choice(vacias) if vacias else None

def encontrar_jugada_ganadora(tablero: List[str], jugador: str) -> Optional[int]:
    for idx in casillas_vacias(tablero):
        copia = tablero[:]
        copia[idx] = jugador
        info = obtener_info_ganador(copia)
        if info and info[0] == jugador:
            return idx
    return None

def cpu_medio() -> Optional[int]:
    cpu = J.turno
    humano = "O" if cpu == "X" else "X"

    ganar = encontrar_jugada_ganadora(J.tablero, cpu)
    if ganar is not None:
        return ganar

    bloquear = encontrar_jugada_ganadora(J.tablero, humano)
    if bloquear is not None:
        return bloquear

    if J.tablero[4] == "":
        return 4

    esquinas = [i for i in [0,2,6,8] if J.tablero[i] == ""]
    if esquinas:
        return random.choice(esquinas)

    lados = [i for i in [1,3,5,7] if J.tablero[i] == ""]
    if lados:
        return random.choice(lados)

    return None

def minimax(tablero: List[str], profundidad: int, es_max: bool, cpu: str, humano: str) -> int:
    info = obtener_info_ganador(tablero)
    if info:
        ganador, _ = info
        if ganador == cpu:
            return 10 - profundidad
        if ganador == humano:
            return profundidad - 10
    if es_empate(tablero):
        return 0

    vacias = casillas_vacias(tablero)

    if es_max:
        mejor = -10**9
        for idx in vacias:
            copia = tablero[:]
            copia[idx] = cpu
            mejor = max(mejor, minimax(copia, profundidad + 1, False, cpu, humano))
        return mejor
    else:
        mejor = 10**9
        for idx in vacias:
            copia = tablero[:]
            copia[idx] = humano
            mejor = min(mejor, minimax(copia, profundidad + 1, True, cpu, humano))
        return mejor

def cpu_dificil_minimax() -> Optional[int]:
    cpu = J.turno
    humano = "O" if cpu == "X" else "X"
    vacias = casillas_vacias(J.tablero)
    if not vacias:
        return None

    mejor_puntaje = -10**9
    mejores = []
    for idx in vacias:
        copia = J.tablero[:]
        copia[idx] = cpu
        puntaje = minimax(copia, 0, False, cpu, humano)
        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejores = [idx]
        elif puntaje == mejor_puntaje:
            mejores.append(idx)

    return random.choice(mejores)

def intentar_jugada_cpu():
    if not J.iniciado or J.bloqueado or J.serie_finalizada:
        return
    if not J.jugadores[J.turno].es_cpu:
        return

    def _hacer():
        jugada = None
        if J.dificultad == "facil":
            jugada = cpu_facil()
        elif J.dificultad == "medio":
            jugada = cpu_medio()
        else:
            jugada = cpu_dificil_minimax()

        if jugada is not None:
            jugar_en(jugada)

    # ✅ FIX: proxy guardado
    setTimeout(guardar_proxy(_hacer), 350)

# =========================
# Construcción tablero y eventos
# =========================

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

        # ✅ FIX: proxy guardado
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

# =========================
# Arranque
# =========================

construir_tablero()
enlazar_eventos()
renderizar_todo()