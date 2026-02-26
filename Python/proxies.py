from pyodide.ffi import create_proxy

# Guardar proxies para que Pyodide NO los destruya (FIX)
PROXIES = []

def guardar_proxy(func):
    p = create_proxy(func)
    PROXIES.append(p)
    return p