# Importamos tipos para poder especificar mejor qué tipo de datos
# reciben y devuelven las funciones (solo ayuda al desarrollo,
# no cambia el comportamiento del programa).
from typing import List, Optional, Tuple


# ==========================================================
# Combinaciones ganadoras del tablero
# ==========================================================
# Cada sublista representa una combinación de índices
# que forman una línea de 3 en el tablero.
#
# El tablero es una lista de 9 posiciones:
#  0 | 1 | 2
#  3 | 4 | 5
#  6 | 7 | 8
#
# Por ejemplo:
# [0,1,2] → fila superior
# [0,4,8] → diagonal principal
LINEAS = [
    [0,1,2],[3,4,5],[6,7,8],      # Filas
    [0,3,6],[1,4,7],[2,5,8],      # Columnas
    [0,4,8],[2,4,6]               # Diagonales
]


# ==========================================================
# Verifica si existe un ganador
# ==========================================================
# tablero: lista con 9 posiciones que contiene:
# "" (vacío), "X" o "O"
#
# Retorna:
# - ("X", [indices]) si X ganó
# - ("O", [indices]) si O ganó
# - None si aún no hay ganador
def obtener_info_ganador(tablero: List[str]) -> Optional[Tuple[str, List[int]]]:
    # Recorremos cada combinación ganadora posible
    for linea in LINEAS:
        a, b, c = linea  # Tomamos los tres índices

        # Verificamos:
        # 1) Que la casilla no esté vacía
        # 2) Que las tres posiciones sean iguales
        if tablero[a] and tablero[a] == tablero[b] == tablero[c]:
            # Si se cumple, retornamos:
            # - Quién ganó (X u O)
            # - Qué línea fue la ganadora
            return tablero[a], linea

    # Si ninguna línea cumple condición, no hay ganador
    return None


# ==========================================================
# Verifica si el tablero está lleno (empate)
# ==========================================================
# Retorna True si ya no quedan casillas vacías.
# No verifica ganador, solo que esté lleno.
def es_empate(tablero: List[str]) -> bool:
    # Comprueba que todas las posiciones sean distintas de ""
    return all(c != "" for c in tablero)


# ==========================================================
# Devuelve las posiciones libres del tablero
# ==========================================================
# Útil para:
# - Saber dónde puede jugar el usuario
# - Saber dónde puede jugar la CPU
# - Usarlo en minimax
#
# Retorna una lista con los índices vacíos.
def casillas_vacias(tablero: List[str]) -> List[int]:
    # Recorremos el tablero con enumerate para obtener:
    # i = índice
    # v = valor en esa posición
    #
    # Si la posición está vacía, guardamos el índice.
    return [i for i, v in enumerate(tablero) if v == ""]