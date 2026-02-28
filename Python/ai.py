from typing import List, Optional
import random
from js import setTimeout

# Estado global del juego
from state import J

# Funciones de reglas del juego
from rules import casillas_vacias, obtener_info_ganador, es_empate

# Proxy para que Pyodide no destruya funciones JS
from proxies import guardar_proxy


# ==========================================================
# CPU NIVEL FÁCIL
# ==========================================================
# Juega completamente al azar.
# Toma una casilla libre random.
def cpu_facil() -> Optional[int]:
    vacias = casillas_vacias(J.tablero)
    # Si hay casillas disponibles, elige una al azar.
    # Si no hay, retorna None.
    return random.choice(vacias) if vacias else None


# ==========================================================
# Busca una jugada ganadora para el jugador indicado
# ==========================================================
# Simula colocar una ficha en cada casilla libre
# y verifica si eso provoca una victoria inmediata.
def encontrar_jugada_ganadora(tablero: List[str], jugador: str) -> Optional[int]:
    for idx in casillas_vacias(tablero):
        copia = tablero[:]          # Copia del tablero
        copia[idx] = jugador        # Simula la jugada

        info = obtener_info_ganador(copia)

        # Si la simulación produce victoria, retornamos esa posición
        if info and info[0] == jugador:
            return idx

    return None


# ==========================================================
# CPU NIVEL MEDIO
# ==========================================================
# Estrategia:
# 1. Intenta ganar si puede
# 2. Si no, bloquea al humano si va a ganar
# 3. Toma el centro si está libre
# 4. Toma una esquina
# 5. Toma un lado
def cpu_medio() -> Optional[int]:
    cpu = J.turno
    humano = "O" if cpu == "X" else "X"

    # 1. Intentar ganar
    ganar = encontrar_jugada_ganadora(J.tablero, cpu)
    if ganar is not None:
        return ganar

    # 2. Bloquear al humano
    bloquear = encontrar_jugada_ganadora(J.tablero, humano)
    if bloquear is not None:
        return bloquear

    # 3. Tomar el centro
    if J.tablero[4] == "":
        return 4

    # 4. Tomar una esquina disponible
    esquinas = [i for i in [0,2,6,8] if J.tablero[i] == ""]
    if esquinas:
        return random.choice(esquinas)

    # 5. Tomar un lado disponible
    lados = [i for i in [1,3,5,7] if J.tablero[i] == ""]
    if lados:
        return random.choice(lados)

    return None


# ==========================================================
# MINIMAX (CPU DIFÍCIL)
# ==========================================================
# Algoritmo recursivo que simula todas las jugadas posibles.
#
# profundidad -> qué tan lejos estamos en el árbol
# es_max -> True si es turno de la CPU, False si es humano
# cpu -> símbolo de la CPU
# humano -> símbolo del oponente
def minimax(tablero: List[str], profundidad: int, es_max: bool, cpu: str, humano: str) -> int:

    # Verificamos si ya hay un ganador
    info = obtener_info_ganador(tablero)
    if info:
        ganador, _ = info

        # Si gana la CPU, valor positivo
        if ganador == cpu:
            return 10 - profundidad

        # Si gana el humano, valor negativo
        if ganador == humano:
            return profundidad - 10

    # Si no hay ganador pero está lleno, es empate
    if es_empate(tablero):
        return 0

    vacias = casillas_vacias(tablero)

    # TURNO DE LA CPU (maximiza)
    if es_max:
        mejor = -10**9  # Valor muy bajo

        for idx in vacias:
            copia = tablero[:]
            copia[idx] = cpu

            # Llamada recursiva para siguiente turno (humano)
            mejor = max(
                mejor,
                minimax(copia, profundidad + 1, False, cpu, humano)
            )

        return mejor

    # TURNO DEL HUMANO (minimiza)
    else:
        mejor = 10**9  # Valor muy alto

        for idx in vacias:
            copia = tablero[:]
            copia[idx] = humano

            mejor = min(
                mejor,
                minimax(copia, profundidad + 1, True, cpu, humano)
            )

        return mejor


# ==========================================================
# CPU DIFÍCIL UTILIZANDO MINIMAX
# ==========================================================
# Evalúa todas las jugadas posibles
# y escoge la mejor según el puntaje.
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

        # Evaluamos el resultado futuro de esta jugada
        puntaje = minimax(copia, 0, False, cpu, humano)

        if puntaje > mejor_puntaje:
            mejor_puntaje = puntaje
            mejores = [idx]
        elif puntaje == mejor_puntaje:
            mejores.append(idx)

    # Si varias jugadas tienen mismo puntaje,
    # elige una aleatoriamente
    return random.choice(mejores)


# ==========================================================
# Ejecuta la jugada de la CPU con retraso visual
# ==========================================================
# jugar_en_callback es la función que realmente hace la jugada.
#
# Se usa setTimeout para simular que la CPU "piensa".
def intentar_jugada_cpu(jugar_en_callback):

    # Validaciones de estado
    if not J.iniciado or J.bloqueado or J.serie_finalizada:
        return

    if not J.jugadores[J.turno].es_cpu:
        return

    def _hacer():
        jugada = None

        # Selección según dificultad
        if J.dificultad == "facil":
            jugada = cpu_facil()
        elif J.dificultad == "medio":
            jugada = cpu_medio()
        else:
            jugada = cpu_dificil_minimax()

        # Ejecuta la jugada elegida
        if jugada is not None:
            jugar_en_callback(jugada)

    # Ejecuta después de 350 ms
    # guardar_proxy evita que Pyodide destruya la función
    setTimeout(guardar_proxy(_hacer), 350)