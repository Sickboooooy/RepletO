// RepletO v2.0 - Main Application Logic
// Manejo de eventos, UI y coordinación entre módulos

// ===============================
// 🎯 CÓDIGO PRECARGADO PARA DEMO
// ===============================

const EJEMPLOS_CODIGO = {
    calculadora_basica: `# RepletO v2.0 - Calculadora Basica
print("Bienvenido a RepletO v2.0!")
print("=" * 50)

# Operaciones matematicas basicas
a = 25
b = 15

print(f"Suma: {a} + {b} = {a + b}")
print(f"Resta: {a} - {b} = {a - b}")
print(f"Multiplicacion: {a} * {b} = {a * b}")
print(f"Division: {a} / {b} = {a / b:.2f}")
print(f"Potencia: {a} ** 2 = {a ** 2}")

# Funciones matematicas
import math
print(f"\\nFunciones avanzadas:")
print(f"Sin(pi/4) = {math.sin(math.pi/4):.4f}")
print(f"Cos(pi/3) = {math.cos(math.pi/3):.4f}")
print(f"Raiz de 64 = {math.sqrt(64)}")

print("\\nRepletO v2.0 funcionando perfectamente!")`,

    calculadora_avanzada: `# RepletO v2.0 - Calculadora Funcional Avanzada
from functools import reduce
import math

print("RepletO v2.0 - Calculadora Funcional Avanzada")
print("=" * 60)

# Operaciones funcionales puras
def sumar(a, b): return a + b
def multiplicar(a, b): return a * b
def potencia(a, b): return a ** b

# Lista de numeros para procesar
numeros = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

print(f"Numeros originales: {numeros}")
print(f"Suma total: {reduce(sumar, numeros)}")
print(f"Producto total: {reduce(multiplicar, numeros)}")

# Operaciones con map y filter
cuadrados = list(map(lambda x: x**2, numeros))
pares = list(filter(lambda x: x % 2 == 0, numeros))

print(f"Cuadrados: {cuadrados}")
print(f"Numeros pares: {pares}")

# Funcion recursiva factorial
def factorial(n):
    return 1 if n <= 1 else n * factorial(n-1)

print(f"\\nFactoriales:")
for i in range(1, 8):
    print(f"factorial({i}) = {factorial(i)}")

print("\\nCalculadora funcional completada!")`
cuadrados = list(map(lambda x: x**2, numeros))
pares = list(filter(lambda x: x % 2 == 0, numeros))

print(f"🔢 Cuadrados: {cuadrados}")
print(f"🔢 Números pares: {pares}")

# Composición de funciones
def componer(f, g):
    return lambda x: f(g(x))

elevar_y_duplicar = componer(lambda x: x * 2, lambda x: x ** 2)

print(f"\\n🎯 Composición f(g(x)) donde g(x)=x² y f(x)=2x:")
for i in range(1, 6):
    resultado = elevar_y_duplicar(i)
    print(f"f(g({i})) = {resultado}")

print("\\n✨ ¡Programación funcional en RepletO v2.0!")`,

    visualizaciones: `# RepletO v2.0 - Visualizaciones Matematicas
import matplotlib.pyplot as plt
import numpy as np

print("RepletO v2.0 - Graficos y Visualizaciones")
print("=" * 50)

# Crear datos para graficos
x = np.linspace(-2*np.pi, 2*np.pi, 100)

# Funciones trigonometricas
y_sin = np.sin(x)
y_cos = np.cos(x)

# Crear grafico
plt.figure(figsize=(12, 8))

# Subplot 1: Funciones trigonometricas
plt.subplot(2, 2, 1)
plt.plot(x, y_sin, 'b-', label='sin(x)', linewidth=2)
plt.plot(x, y_cos, 'r-', label='cos(x)', linewidth=2)
plt.title('Funciones Trigonometricas')
plt.xlabel('x')
plt.ylabel('y')
plt.legend()
plt.grid(True, alpha=0.3)

# Subplot 2: Funcion cuadratica
x2 = np.linspace(-5, 5, 100)
y_quad = x2**2
plt.subplot(2, 2, 2)
plt.plot(x2, y_quad, 'g-', linewidth=2)
plt.title('Funcion Cuadratica: y = x²')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)

# Subplot 3: Distribucion normal
x3 = np.linspace(-4, 4, 100)
y_normal = (1/np.sqrt(2*np.pi)) * np.exp(-0.5 * x3**2)
plt.subplot(2, 2, 3)
plt.plot(x3, y_normal, 'm-', linewidth=2)
plt.fill_between(x3, y_normal, alpha=0.3)
plt.title('Distribucion Normal')
plt.xlabel('x')
plt.ylabel('Densidad')
plt.grid(True, alpha=0.3)

# Subplot 4: Datos aleatorios
np.random.seed(42)
x4 = np.random.randn(50)
y4 = 2 * x4 + np.random.randn(50) * 0.5
plt.subplot(2, 2, 4)
plt.scatter(x4, y4, alpha=0.6, c='red')
plt.title('Datos Aleatorios')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('graficos_repleto.png')
print("Graficos guardados en: graficos_repleto.png")
plt.show()

print("RepletO v2.0 - Graficos cientificos funcionando")`

# Subplot 2: Función cuadrática
plt.subplot(2, 2, 2)
x2 = np.linspace(-5, 5, 100)
y2 = x2**2
plt.plot(x2, y2, 'g-', linewidth=3)
plt.title('📐 Función Cuadrática: y = x²')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)

# Subplot 3: Función exponencial
plt.subplot(2, 2, 3)
x3 = np.linspace(-2, 2, 100)
y3 = np.exp(x3)
plt.plot(x3, y3, 'm-', linewidth=2)
plt.title('🚀 Función Exponencial: y = eˣ')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)

# Subplot 4: Campana de Gauss
plt.subplot(2, 2, 4)
x4 = np.linspace(-3, 3, 100)
y4 = np.exp(-x4**2)
plt.plot(x4, y4, 'orange', linewidth=3)
plt.fill_between(x4, y4, alpha=0.3, color='orange')
plt.title('🔔 Campana de Gauss: y = e^(-x²)')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("✅ ¡Visualizaciones generadas exitosamente!")
print("🎨 RepletO v2.0 - Gráficos científicos funcionando")`,

    fibonacci: `# 🌟 Secuencia de Fibonacci - Algoritmos Eficientes
print("🔥 RepletO v2.0 - Algoritmos Avanzados")
print("🌀 Secuencia de Fibonacci con diferentes enfoques")
print("=" * 60)

# Método 1: Recursivo (ineficiente pero elegante)
def fibonacci_recursivo(n):
    if n <= 1:
        return n
    return fibonacci_recursivo(n-1) + fibonacci_recursivo(n-2)

# Método 2: Iterativo (eficiente)
def fibonacci_iterativo(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Método 3: Con memoización (elegante y eficiente)
def fibonacci_memo(n, memo={}):
    if n in memo:
        return memo[n]
    if n <= 1:
        memo[n] = n
    else:
        memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n-2, memo)
    return memo[n]

# Generar secuencia
print("📊 Primeros 15 números de Fibonacci:")
for i in range(15):
    fib = fibonacci_iterativo(i)
    print(f"F({i:2d}) = {fib:8d}")

# Comparar métodos para números grandes
n = 30
print(f"\\n🚀 Fibonacci({n}) con diferentes métodos:")

import time

# Método iterativo
start = time.time()
result_iter = fibonacci_iterativo(n)
time_iter = time.time() - start

# Método con memoización  
start = time.time()
result_memo = fibonacci_memo(n)
time_memo = time.time() - start

print(f"⚡ Iterativo: {result_iter} (tiempo: {time_iter:.6f}s)")
print(f"🧠 Memoización: {result_memo} (tiempo: {time_memo:.6f}s)")

# Razón áurea en Fibonacci
print(f"\\n🌟 Razón áurea en Fibonacci:")
for i in range(10, 15):
    a, b = fibonacci_iterativo(i), fibonacci_iterativo(i+1)
    ratio = b / a if a != 0 else 0
    print(f"F({i+1})/F({i}) = {ratio:.8f}")

phi = (1 + 5**0.5) / 2
print(f"\\n✨ Razón áurea exacta: φ = {phi:.8f}")
print("🎯 ¡Los ratios convergen a φ!")`,

    data_science: `# 🔬 Data Science con RepletO v2.0
import numpy as np
import matplotlib.pyplot as plt

print("📊 RepletO v2.0 - Análisis de Datos")
print("=" * 50)

# Generar datos sintéticos
np.random.seed(42)
n_samples = 1000

# Dataset 1: Datos normales
datos_normales = np.random.normal(50, 15, n_samples)

# Dataset 2: Datos con tendencia
x = np.linspace(0, 10, n_samples)
y = 2*x + 5 + np.random.normal(0, 2, n_samples)

print("📈 Estadísticas descriptivas:")
print(f"Media: {np.mean(datos_normales):.2f}")
print(f"Mediana: {np.median(datos_normales):.2f}")
print(f"Desviación estándar: {np.std(datos_normales):.2f}")
print(f"Mínimo: {np.min(datos_normales):.2f}")
print(f"Máximo: {np.max(datos_normales):.2f}")

# Análisis de correlación
correlacion = np.corrcoef(x, y)[0, 1]
print(f"\\n🔗 Correlación x-y: {correlacion:.4f}")

# Visualizaciones
plt.figure(figsize=(15, 10))

# Histograma
plt.subplot(2, 3, 1)
plt.hist(datos_normales, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
plt.title('📊 Distribución Normal')
plt.xlabel('Valor')
plt.ylabel('Frecuencia')
plt.grid(True, alpha=0.3)

# Scatter plot
plt.subplot(2, 3, 2)
plt.scatter(x, y, alpha=0.6, s=20, color='coral')
plt.title('🎯 Scatter Plot con Tendencia')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True, alpha=0.3)

# Box plot
plt.subplot(2, 3, 3)
plt.boxplot(datos_normales)
plt.title('📦 Box Plot')
plt.ylabel('Valores')
plt.grid(True, alpha=0.3)

# Serie temporal
plt.subplot(2, 3, 4)
time_series = np.cumsum(np.random.randn(100))
plt.plot(time_series, linewidth=2, color='green')
plt.title('📈 Serie Temporal')
plt.xlabel('Tiempo')
plt.ylabel('Valor')
plt.grid(True, alpha=0.3)

# Heatmap simple
plt.subplot(2, 3, 5)
data_2d = np.random.randn(10, 10)
plt.imshow(data_2d, cmap='viridis', aspect='auto')
plt.colorbar()
plt.title('🌡️ Heatmap')

# Función matemática compleja
plt.subplot(2, 3, 6)
x_func = np.linspace(-5, 5, 200)
y_func = np.sin(x_func) * np.exp(-x_func**2/10)
plt.plot(x_func, y_func, linewidth=3, color='purple')
plt.title('🌊 sin(x) × e^(-x²/10)')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

print("\\n✅ Análisis de datos completado!")
print("🎨 RepletO v2.0 - Data Science funcionando perfectamente")`
};

// ===============================
// 🎮 VARIABLES GLOBALES
// ===============================

let outputContainer = null;
let runButton = null;
let clearButton = null;
let clearOutputButton = null;
let loadingOverlay = null;
let isExecuting = false;

// Configuración de la aplicación
const APP_CONFIG = {
    maxOutputEntries: 50,
    autoScrollOutput: true,
    saveHistory: true,
    showTimestamps: true,
    enableKeyboardShortcuts: true
};

// ===============================
// 🚀 INICIALIZACIÓN
// ===============================

/**
 * Inicializa la aplicación principal
 */
function initializeApp() {
    console.log('🚀 Inicializando RepletO v2.0...');
    
    // Obtener referencias a elementos DOM
    getElementReferences();
    
    // Crear selector de ejemplos
    createExampleSelector();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Configurar atajos de teclado
    setupKeyboardShortcuts();
    
    // Configurar resizer de paneles
    setupPanelResizer();
    
    // Verificar estado del servidor
    checkServerStatus();
    
    // Cargar ejemplo por defecto
    setTimeout(() => {
        loadExample('calculadora_basica');
    }, 1000);
    
    console.log('✅ RepletO v2.0 inicializado correctamente');
}

/**
 * Obtiene referencias a elementos DOM importantes
 */
function getElementReferences() {
    outputContainer = document.getElementById('output');
    runButton = document.getElementById('runBtn');
    clearButton = document.getElementById('clearBtn');
    clearOutputButton = document.getElementById('clearOutputBtn');
    loadingOverlay = document.getElementById('loadingOverlay');
    
    // Verificar que todos los elementos existen
    const requiredElements = {
        outputContainer,
        runButton,
        clearButton,
        clearOutputButton,
        loadingOverlay
    };
    
    for (const [name, element] of Object.entries(requiredElements)) {
        if (!element) {
            console.error(`Elemento requerido no encontrado: ${name}`);
        }
    }
}

// ===============================
// 🎯 GESTIÓN DE EJEMPLOS
// ===============================

/**
 * Crea el selector de ejemplos en la interfaz
 */
function createExampleSelector() {
    const headerActions = document.querySelector('.header-actions');
    if (!headerActions) return;
    
    const selectorContainer = document.createElement('div');
    selectorContainer.style.marginRight = '10px';
    selectorContainer.innerHTML = `
        <select id="exampleSelector" style="
            padding: 8px 12px;
            border: 1px solid #444;
            background: #2d2d2d;
            color: #fff;
            border-radius: 5px;
            font-size: 12px;
            cursor: pointer;
        ">
            <option value="">📚 Seleccionar ejemplo...</option>
            <option value="calculadora_basica">Calculadora Basica</option>
            <option value="calculadora_avanzada">Calculadora Avanzada</option>
            <option value="visualizaciones">Visualizaciones</option>
            <option value="fibonacci">Fibonacci</option>
            <option value="data_science">Data Science</option>
        </select>
    `;
    
    headerActions.insertBefore(selectorContainer, headerActions.firstChild);
    
    document.getElementById('exampleSelector').addEventListener('change', function(e) {
        if (e.target.value) {
            loadExample(e.target.value);
            e.target.value = ''; // Reset selector
        }
    });
}

/**
 * Carga un ejemplo de código en el editor
 */
function loadExample(nombreEjemplo) {
    if (EJEMPLOS_CODIGO[nombreEjemplo]) {
        if (window.setEditorValue) {
            window.setEditorValue(EJEMPLOS_CODIGO[nombreEjemplo]);
            console.log(`📖 Ejemplo cargado: ${nombreEjemplo}`);
            
            // Focus en el editor si está disponible
            if (window.focusEditor) {
                window.focusEditor();
            }
        } else {
            console.warn('setEditorValue no disponible');
        }
    }
}

// ===============================
// 🎮 EVENT LISTENERS
// ===============================

/**
 * Configura los event listeners principales
 */
function setupEventListeners() {
    // Botón ejecutar
    if (runButton) {
        runButton.addEventListener('click', handleRunCode);
    }
    
    // Botón limpiar editor
    if (clearButton) {
        clearButton.addEventListener('click', handleClearEditor);
    }
    
    // Botón limpiar output
    if (clearOutputButton) {
        clearOutputButton.addEventListener('click', handleClearOutput);
    }
    
    // Eventos personalizados del editor
    window.addEventListener('runCode', handleRunCode);
    window.addEventListener('clearOutput', handleClearOutput);
    window.addEventListener('editorReady', handleEditorReady);
    
    // Eventos de estado de red
    window.addEventListener('online', handleNetworkOnline);
    window.addEventListener('offline', handleNetworkOffline);
    
    // Evento antes de cerrar la página
    window.addEventListener('beforeunload', handleBeforeUnload);
}

/**
 * Configura atajos de teclado globales
 */
function setupKeyboardShortcuts() {
    if (!APP_CONFIG.enableKeyboardShortcuts) return;
    
    document.addEventListener('keydown', (event) => {
        // Ctrl+Enter o Cmd+Enter - Ejecutar código
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            handleRunCode();
        }
        
        // Ctrl+L o Cmd+L - Limpiar output
        if ((event.ctrlKey || event.metaKey) && event.key === 'l') {
            event.preventDefault();
            handleClearOutput();
        }
        
        // Escape - Detener ejecución (si está corriendo)
        if (event.key === 'Escape' && isExecuting) {
            event.preventDefault();
            // Opcional: implementar cancelación
            console.log('Intento de cancelar ejecución');
        }
    });
}

/**
 * Configura el resizer de paneles
 */
function setupPanelResizer() {
    const resizer = document.getElementById('resizer');
    const editorPanel = document.querySelector('.editor-panel');
    const outputPanel = document.querySelector('.output-panel');
    
    if (!resizer || !editorPanel || !outputPanel) return;
    
    let isResizing = false;
    
    resizer.addEventListener('mousedown', (e) => {
        isResizing = true;
        resizer.classList.add('dragging');
        document.body.style.cursor = 'col-resize';
        document.body.style.userSelect = 'none';
    });
    
    document.addEventListener('mousemove', (e) => {
        if (!isResizing) return;
        
        const containerRect = document.querySelector('.main-content').getBoundingClientRect();
        const percentage = ((e.clientX - containerRect.left) / containerRect.width) * 100;
        
        // Limitar el porcentaje entre 20% y 80%
        const clampedPercentage = Math.max(20, Math.min(80, percentage));
        
        editorPanel.style.flexBasis = `${clampedPercentage}%`;
        outputPanel.style.flexBasis = `${100 - clampedPercentage}%`;
        
        // Redimensionar editor Monaco
        setTimeout(() => {
            if (window.resizeEditor) {
                window.resizeEditor();
            }
        }, 10);
    });
    
    document.addEventListener('mouseup', () => {
        if (isResizing) {
            isResizing = false;
            resizer.classList.remove('dragging');
            document.body.style.cursor = '';
            document.body.style.userSelect = '';
        }
    });
}

// ===============================
// 🏃‍♂️ MANEJO DE EJECUCIÓN
// ===============================

/**
 * Maneja la ejecución de código
 */
async function handleRunCode() {
    if (isExecuting) {
        console.log('Ya hay una ejecución en progreso');
        return;
    }
    
    // Verificar que el editor esté listo
    if (!window.getEditorValue) {
        showOutputError('Editor no está listo');
        return;
    }
    
    const code = window.getEditorValue();
    
    if (!code.trim()) {
        showOutputError('No hay código para ejecutar');
        return;
    }
    
    try {
        // Marcar como ejecutando
        setExecutionState(true);
        
        // Ejecutar código
        const result = await window.executeCode(code);
        
        // Mostrar resultado
        displayExecutionResult(result);
        
    } catch (error) {
        console.error('Error en ejecución:', error);
        showOutputError(`Error inesperado: ${error.message}`);
    } finally {
        // Marcar como no ejecutando
        setExecutionState(false);
    }
}

/**
 * Maneja la limpieza del editor
 */
function handleClearEditor() {
    if (window.clearEditor) {
        window.clearEditor();
        console.log('Editor limpiado');
    }
}

/**
 * Maneja la limpieza del output
 */
function handleClearOutput() {
    if (outputContainer) {
        outputContainer.innerHTML = `
            <div class="output-placeholder">
                <div class="placeholder-icon">📝</div>
                <p>La salida de tu código aparecerá aquí...</p>
                <p class="placeholder-hint">Tip: Usa Ctrl+Enter para ejecutar</p>
            </div>
        `;
        console.log('Output limpiado');
    }
}

/**
 * Maneja cuando el editor está listo
 */
function handleEditorReady(event) {
    console.log('Editor listo:', event.detail);
    
    // Cargar ejemplo por defecto después de que el editor esté listo
    setTimeout(() => {
        loadExample('calculadora_basica');
    }, 500);
}

/**
 * Maneja cuando la red vuelve online
 */
function handleNetworkOnline() {
    console.log('Conexión restaurada');
    checkServerStatus();
}

/**
 * Maneja cuando la red va offline
 */
function handleNetworkOffline() {
    console.log('Conexión perdida');
}

/**
 * Maneja antes de cerrar la página
 */
function handleBeforeUnload(event) {
    if (isExecuting) {
        const message = '¿Estás seguro? Hay código ejecutándose.';
        event.returnValue = message;
        return message;
    }
}

// ===============================
// 🎨 MANEJO DE UI
// ===============================

/**
 * Establece el estado de ejecución
 */
function setExecutionState(executing) {
    isExecuting = executing;
    
    // Actualizar UI
    if (runButton) {
        runButton.disabled = executing;
        if (executing) {
            runButton.innerHTML = `
                <span class="icon">⏳</span>
                Ejecutando...
            `;
        } else {
            runButton.innerHTML = `
                <span class="icon">▶️</span>
                Ejecutar
                <span class="shortcut">Ctrl+Enter</span>
            `;
        }
    }
    
    // Mostrar/ocultar overlay de carga
    if (loadingOverlay) {
        if (executing) {
            loadingOverlay.classList.remove('hidden');
        } else {
            loadingOverlay.classList.add('hidden');
        }
    }
}

/**
 * Muestra el resultado de la ejecución
 */
function displayExecutionResult(result) {
    if (!outputContainer) return;
    
    // Limpiar placeholder si existe
    const placeholder = outputContainer.querySelector('.output-placeholder');
    if (placeholder) {
        placeholder.remove();
    }
    
    // Crear entrada de output
    const entry = createOutputEntry(result);
    outputContainer.appendChild(entry);
    
    // Limitar número de entradas
    limitOutputEntries();
    
    // Auto-scroll si está habilitado
    if (APP_CONFIG.autoScrollOutput) {
        scrollToBottom();
    }
}

/**
 * Crea una entrada de output
 */
function createOutputEntry(result) {
    const entry = document.createElement('div');
    entry.className = `output-entry ${result.status}`;
    
    const timestamp = new Date(result.timestamp).toLocaleTimeString();
    const statusIcon = result.status === 'success' ? '✅' : '❌';
    const statusText = result.status === 'success' ? 'Éxito' : 'Error';
    
    entry.innerHTML = `
        <div class="output-header">
            <div class="output-status">
                <span class="status-icon ${result.status}">${statusIcon}</span>
                <span>${statusText}</span>
            </div>
            ${APP_CONFIG.showTimestamps ? `<span class="timestamp">${timestamp}</span>` : ''}
        </div>
        <div class="output-content ${result.error ? 'output-error' : ''}">
            ${escapeHtml(result.error || result.output || 'Sin salida')}
        </div>
    `;
    
    return entry;
}

/**
 * Muestra un error en el output
 */
function showOutputError(message) {
    const result = {
        status: 'error',
        output: '',
        error: message,
        timestamp: new Date().toISOString()
    };
    
    displayExecutionResult(result);
}

/**
 * Limita el número de entradas en el output
 */
function limitOutputEntries() {
    if (!outputContainer) return;
    
    const entries = outputContainer.querySelectorAll('.output-entry');
    if (entries.length > APP_CONFIG.maxOutputEntries) {
        const excess = entries.length - APP_CONFIG.maxOutputEntries;
        for (let i = 0; i < excess; i++) {
            entries[i].remove();
        }
    }
}

/**
 * Hace scroll al final del output
 */
function scrollToBottom() {
    if (outputContainer) {
        outputContainer.scrollTop = outputContainer.scrollHeight;
    }
}

// ===============================
// 🔍 UTILIDADES
// ===============================

/**
 * Verifica el estado del servidor
 */
async function checkServerStatus() {
    try {
        const health = await window.checkHealth();
        console.log('Estado del servidor:', health.status);
        
        // Opcional: actualizar indicador visual
        updateServerStatusIndicator(health.status === 'online');
        
    } catch (error) {
        console.error('Error verificando servidor:', error);
        updateServerStatusIndicator(false);
    }
}

/**
 * Actualiza el indicador visual del estado del servidor
 */
function updateServerStatusIndicator(isOnline) {
    console.log(`Servidor: ${isOnline ? 'Online ✅' : 'Offline ❌'}`);
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===============================
// 🎬 INICIALIZACIÓN FINAL
// ===============================

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Exportar funciones principales para uso global
window.handleRunCode = handleRunCode;
window.handleClearOutput = handleClearOutput;
window.handleClearEditor = handleClearEditor;
window.loadExample = loadExample;