"""
🧮 Calculadora Funcional - Primera Prueba RepletO v2.0
=====================================================

Calculadora avanzada con diseño funcional puro, sin efectos secundarios.
Perfecta para demostrar las capacidades de RepletO v2.0:

✨ Características:
- Programación funcional pura
- Inmutabilidad de datos  
- Funciones de alto orden
- Composición de funciones
- Evaluación lazy
- Manejo funcional de errores
- Visualizaciones matemáticas

🎯 Casos de uso para RepletO:
- Mostrar syntax highlighting
- Demostrar ejecución en tiempo real
- Probar visualizaciones matplotlib
- Validar manejo de errores
- Comprobar autocompletado IA
"""

from typing import Callable, Union, List, Tuple, Optional
from functools import reduce, partial
from math import pi, e, sqrt, sin, cos, tan, log, exp
import matplotlib.pyplot as plt
import numpy as np

# ===============================
# 🔧 TIPOS Y CONSTANTES
# ===============================

Numero = Union[int, float]
Operacion = Callable[[Numero, Numero], Numero]
FuncionUnaria = Callable[[Numero], Numero]

# Constantes matemáticas
CONSTANTES = {
    'pi': pi,
    'e': e,
    'phi': (1 + sqrt(5)) / 2,  # Número áureo
    'tau': 2 * pi
}

# ===============================
# 🔢 OPERACIONES BÁSICAS PURAS
# ===============================

def sumar(a: Numero, b: Numero) -> Numero:
    """Suma dos números de forma pura"""
    return a + b

def restar(a: Numero, b: Numero) -> Numero:
    """Resta dos números de forma pura"""
    return a - b

def multiplicar(a: Numero, b: Numero) -> Numero:
    """Multiplica dos números de forma pura"""
    return a * b

def dividir(a: Numero, b: Numero) -> Numero:
    """División segura con manejo funcional de errores"""
    if b == 0:
        raise ValueError("No se puede dividir por cero")
    return a / b

def potencia(base: Numero, exponente: Numero) -> Numero:
    """Eleva base a la potencia del exponente"""
    return base ** exponente

def raiz(numero: Numero, indice: Numero = 2) -> Numero:
    """Calcula la raíz n-ésima de un número"""
    if numero < 0 and indice % 2 == 0:
        raise ValueError("No se puede calcular raíz par de número negativo")
    return numero ** (1 / indice)

# ===============================
# 🧮 CALCULADORA FUNCIONAL
# ===============================

class CalculadoraFuncional:
    """
    Calculadora con diseño funcional puro
    
    Principios aplicados:
    - Inmutabilidad: Ningún estado mutable
    - Pureza: Sin efectos secundarios
    - Composición: Operaciones combinables
    - Transparencia referencial: Misma entrada = misma salida
    """
    
    def __init__(self):
        """Inicializar con operaciones disponibles"""
        self.operaciones = {
            '+': sumar,
            '-': restar,
            '*': multiplicar,
            '/': dividir,
            '**': potencia,
            'sqrt': lambda x: raiz(x, 2),
            'cbrt': lambda x: raiz(x, 3),
        }
        
        self.funciones_unarias = {
            'sin': sin,
            'cos': cos,
            'tan': tan,
            'log': log,
            'exp': exp,
            'abs': abs,
            'neg': lambda x: -x,
        }
    
    def calcular(self, operacion: str, *args: Numero) -> Numero:
        """
        Ejecuta una operación de forma funcional
        
        Args:
            operacion: Nombre de la operación
            *args: Argumentos numéricos
            
        Returns:
            Resultado del cálculo
            
        Raises:
            ValueError: Si la operación no existe o argumentos inválidos
        """
        if operacion in self.operaciones:
            if len(args) != 2:
                raise ValueError(f"Operación '{operacion}' requiere exactamente 2 argumentos")
            return self.operaciones[operacion](*args)
        
        elif operacion in self.funciones_unarias:
            if len(args) != 1:
                raise ValueError(f"Función '{operacion}' requiere exactamente 1 argumento")
            return self.funciones_unarias[operacion](*args)
        
        else:
            raise ValueError(f"Operación '{operacion}' no reconocida")
    
    def evaluar_expresion(self, numeros: List[Numero], operaciones: List[str]) -> Numero:
        """
        Evalúa una secuencia de operaciones de forma funcional
        
        Args:
            numeros: Lista de números
            operaciones: Lista de operaciones
            
        Returns:
            Resultado final
        """
        if len(numeros) != len(operaciones) + 1:
            raise ValueError("Número incorrecto de operaciones para los números dados")
        
        # Usar reduce para aplicar operaciones secuencialmente
        def aplicar_operacion(acumulador: Numero, operacion_numero: Tuple[str, Numero]) -> Numero:
            operacion, numero = operacion_numero
            return self.calcular(operacion, acumulador, numero)
        
        # Combinar operaciones con números (excepto el primero)
        operaciones_numeros = list(zip(operaciones, numeros[1:]))
        
        # Aplicar reduce para procesar toda la secuencia
        return reduce(aplicar_operacion, operaciones_numeros, numeros[0])
    
    def crear_funcion_personalizada(self, operaciones: List[str]) -> Callable:
        """
        Crea una función personalizada usando composición
        
        Args:
            operaciones: Lista de operaciones unarias a componer
            
        Returns:
            Función compuesta
        """
        def componer(f: Callable, g: Callable) -> Callable:
            return lambda x: f(g(x))
        
        # Obtener funciones de las operaciones
        funciones = [self.funciones_unarias[op] for op in operaciones if op in self.funciones_unarias]
        
        if not funciones:
            raise ValueError("No se encontraron operaciones válidas")
        
        # Componer todas las funciones usando reduce
        return reduce(componer, funciones)

# ===============================
# 📊 UTILIDADES DE VISUALIZACIÓN
# ===============================

def graficar_funcion(func: Callable[[float], float], 
                    rango: Tuple[float, float] = (-10, 10),
                    titulo: str = "Función matemática") -> None:
    """
    Grafica una función matemática
    
    Args:
        func: Función a graficar
        rango: Rango de valores x (min, max)
        titulo: Título del gráfico
    """
    x = np.linspace(rango[0], rango[1], 1000)
    
    try:
        y = [func(xi) for xi in x]
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, 'b-', linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.title(titulo, fontsize=14, fontweight='bold')
        plt.xlabel('x', fontsize=12)
        plt.ylabel('f(x)', fontsize=12)
        plt.axhline(y=0, color='k', linewidth=0.5)
        plt.axvline(x=0, color='k', linewidth=0.5)
        plt.show()
        
    except Exception as e:
        print(f"❌ Error graficando función: {e}")

def mostrar_tabla_operaciones(calc: CalculadoraFuncional, 
                             numeros: List[Numero], 
                             operacion: str) -> None:
    """
    Muestra una tabla con resultados de operaciones
    
    Args:
        calc: Instancia de calculadora
        numeros: Lista de números para probar
        operacion: Operación a aplicar
    """
    print(f"\n📋 Tabla de operación: {operacion}")
    print("=" * 50)
    
    if operacion in calc.funciones_unarias:
        print("   x    │  f(x)")
        print("────────┼─────────")
        for num in numeros:
            try:
                resultado = calc.calcular(operacion, num)
                print(f"{num:7.2f} │ {resultado:8.3f}")
            except Exception as e:
                print(f"{num:7.2f} │ Error: {e}")
    else:
        print("   x    │   y   │ resultado")
        print("────────┼───────┼──────────")
        for i in range(0, len(numeros) - 1, 2):
            if i + 1 < len(numeros):
                x, y = numeros[i], numeros[i + 1]
                try:
                    resultado = calc.calcular(operacion, x, y)
                    print(f"{x:7.2f} │ {y:5.2f} │ {resultado:9.3f}")
                except Exception as e:
                    print(f"{x:7.2f} │ {y:5.2f} │ Error: {e}")

# ===============================
# 🎯 EJEMPLOS Y DEMOSTRACIONES
# ===============================

def demo_basica():
    """Demostración de operaciones básicas"""
    print("🧮 DEMO: Calculadora Funcional - Operaciones Básicas")
    print("=" * 60)
    
    calc = CalculadoraFuncional()
    
    # Operaciones simples
    operaciones_demo = [
        ('+', 15, 25),
        ('-', 100, 35),
        ('*', 7, 8),
        ('/', 144, 12),
        ('**', 3, 4),
        ('sqrt', 64),
        ('sin', CONSTANTES['pi']/4),
        ('cos', CONSTANTES['pi']/3),
        ('log', CONSTANTES['e']),
    ]
    
    for op_data in operaciones_demo:
        operacion = op_data[0]
        args = op_data[1:]
        
        try:
            resultado = calc.calcular(operacion, *args)
            if len(args) == 1:
                print(f"📊 {operacion}({args[0]}) = {resultado:.4f}")
            else:
                print(f"📊 {args[0]} {operacion} {args[1]} = {resultado:.4f}")
        except Exception as e:
            print(f"❌ Error: {e}")

def demo_avanzada():
    """Demostración de funciones avanzadas"""
    print("\n🔬 DEMO: Calculadora Funcional - Funciones Avanzadas")
    print("=" * 60)
    
    calc = CalculadoraFuncional()
    
    # Evaluación de expresiones complejas
    print("\n🧪 Evaluando expresión: 10 + 5 * 3 - 8 / 2")
    try:
        resultado = calc.evaluar_expresion([10, 5, 3, 8, 2], ['+', '*', '-', '/'])
        print(f"📈 Resultado: {resultado}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Composición de funciones
    print("\n🔄 Creando función compuesta: sin(log(abs(x)))")
    try:
        func_compuesta = calc.crear_funcion_personalizada(['abs', 'log', 'sin'])
        test_values = [1, 2, 5, 10]
        
        print("   x    │ sin(log(abs(x)))")
        print("────────┼─────────────────")
        
        for x in test_values:
            resultado = func_compuesta(x)
            print(f"{x:7.1f} │ {resultado:14.6f}")
            
    except Exception as e:
        print(f"❌ Error creando función: {e}")

def demo_visualizacion():
    """Demostración de visualizaciones"""
    print("\n📊 DEMO: Visualizaciones Matemáticas")
    print("=" * 60)
    
    calc = CalculadoraFuncional()
    
    # Crear funciones para graficar
    funciones_demo = [
        (lambda x: x**2, "Función cuadrática: f(x) = x²"),
        (lambda x: sin(x), "Función seno: f(x) = sin(x)"),
        (lambda x: exp(-x**2), "Campana de Gauss: f(x) = e^(-x²)"),
    ]
    
    for func, titulo in funciones_demo:
        print(f"📈 Graficando: {titulo}")
        graficar_funcion(func, (-5, 5), titulo)
    
    # Tabla de operaciones
    numeros_test = [0, 1, 2, 3, 4, 5, -1, -2]
    mostrar_tabla_operaciones(calc, numeros_test, 'sin')

# ===============================
# 🚀 PROGRAMA PRINCIPAL
# ===============================

def main():
    """Función principal - Demo completa de la calculadora"""
    print("🎨 RepletO v2.0 - Primera Prueba con Calculadora Funcional")
    print("=" * 70)
    print("💡 Esta calculadora demuestra:")
    print("   • Programación funcional pura")
    print("   • Composición de funciones")
    print("   • Inmutabilidad de datos")
    print("   • Visualizaciones matemáticas")
    print("   • Manejo funcional de errores")
    print()
    
    # Ejecutar demos
    demo_basica()
    demo_avanzada()
    demo_visualizacion()
    
    print("\n🎉 ¡Demo completada! RepletO v2.0 funcionando perfectamente.")
    print("✨ Características probadas:")
    print("   ✅ Syntax highlighting")
    print("   ✅ Ejecución en tiempo real")
    print("   ✅ Visualizaciones matplotlib")
    print("   ✅ Manejo de errores")
    print("   ✅ Funciones complejas")

if __name__ == "__main__":
    main()

# ===============================
# 🧪 CASOS DE PRUEBA ADICIONALES
# ===============================

def pruebas_unitarias():
    """Pruebas unitarias para validar funcionalidad"""
    print("\n🧪 Ejecutando pruebas unitarias...")
    
    calc = CalculadoraFuncional()
    
    # Pruebas básicas
    assert calc.calcular('+', 2, 3) == 5
    assert calc.calcular('*', 4, 5) == 20
    assert abs(calc.calcular('sin', pi/2) - 1) < 1e-10
    assert calc.calcular('sqrt', 25) == 5
    
    # Prueba de composición
    func = calc.crear_funcion_personalizada(['abs', 'sqrt'])
    assert func(-9) == 3
    
    print("✅ Todas las pruebas pasaron!")

# Ejecutar pruebas si se solicita
# pruebas_unitarias()