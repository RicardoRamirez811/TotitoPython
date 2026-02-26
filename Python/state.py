from dataclasses import dataclass
from typing import List, Optional, Callable

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

# Instancia global (misma idea que tu archivo original)
J = EstadoJuego()