from js import document

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