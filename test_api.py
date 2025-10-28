import requests
import json

# Probar API de RepletO
url = "http://localhost:8000/api/execute"

codigo_prueba = """
print("=== PRUEBA REPLETO V2.0 ===")
print("Hola desde RepletO!")

# Variables
nombre = "Usuario"
print(f"Bienvenido, {nombre}!")

# Operaciones
a = 10
b = 5
print(f"Suma: {a} + {b} = {a + b}")
print(f"Multiplicacion: {a} * {b} = {a * b}")

# Lista
numeros = [1, 2, 3, 4, 5]
print(f"Numeros: {numeros}")
print(f"Suma total: {sum(numeros)}")

print("=== EJECUCION COMPLETADA ===")
"""

data = {"code": codigo_prueba}

try:
    print("Enviando solicitud a RepletO...")
    response = requests.post(url, json=data, timeout=15)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['status']}")
        print("OUTPUT:")
        print(result['output'])
        if result.get('error'):
            print("ERROR:")
            print(result['error'])
    else:
        print(f"Error HTTP: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error de conexion: {e}")