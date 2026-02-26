from typing import List, Optional
import random
from js import setTimeout

from state import J
from rules import casillas_vacias, obtener_info_ganador, es_empate
from proxies import guardar_proxy

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

def intentar_jugada_cpu(jugar_en_callback):
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
            jugar_en_callback(jugada)

    setTimeout(guardar_proxy(_hacer), 350)