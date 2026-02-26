from typing import List, Optional, Tuple

LINEAS = [
    [0,1,2],[3,4,5],[6,7,8],
    [0,3,6],[1,4,7],[2,5,8],
    [0,4,8],[2,4,6]
]

def obtener_info_ganador(tablero: List[str]) -> Optional[Tuple[str, List[int]]]:
    for linea in LINEAS:
        a, b, c = linea
        if tablero[a] and tablero[a] == tablero[b] == tablero[c]:
            return tablero[a], linea
    return None

def es_empate(tablero: List[str]) -> bool:
    return all(c != "" for c in tablero)

def casillas_vacias(tablero: List[str]) -> List[int]:
    return [i for i, v in enumerate(tablero) if v == ""]