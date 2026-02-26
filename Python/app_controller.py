from js import document, console

from setup import construir_tablero, enlazar_eventos
from ui_render import renderizar_todo

class AppTresEnRaya:
    #def __init__(self):
    #    console.log("✅ PyScript cargó (modular)")
    #    document.body.insertAdjacentHTML(
    #        "afterbegin",
    #        "<div class='alert alert-info m-2'>✅ Python (PyScript) cargado</div>"
    #    )

    def iniciar(self):
        construir_tablero()
        enlazar_eventos()
        renderizar_todo()