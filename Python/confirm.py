from typing import Callable
from state import J
from dom_utils import texto, mostrar, ocultar

def pedir_confirmacion(mensaje: str, accion: Callable[[], None]):
    J.accion_pendiente = accion
    texto("textoConfirmacion", mensaje)
    mostrar("cajaConfirmacion")

def ocultar_confirmacion():
    J.accion_pendiente = None
    ocultar("cajaConfirmacion")