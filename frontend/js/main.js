// RepletO - Main Application Logic
// Manejo de eventos, UI y coordinación entre módulos

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

/**
 * Inicializa la aplicación principal
 */
function initializeApp() {
    console.log('🚀 Inicializando RepletO...');
    
    // Obtener referencias a elementos DOM
    getElementReferences();
    
    // Configurar event listeners
    setupEventListeners();
    
    // Configurar atajos de teclado
    setupKeyboardShortcuts();
    
    // Configurar resizer de paneles
    setupPanelResizer();
    
    // Verificar estado del servidor
    checkServerStatus();
    
    console.log('✅ RepletO inicializado correctamente');
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
    
    // Opcional: cargar código guardado
    // const savedCode = localStorage.getItem('repleto-editor-content');
    // if (savedCode && window.setEditorValue) {
    //     window.setEditorValue(savedCode);
    // }
}

/**
 * Maneja cuando la red vuelve online
 */
function handleNetworkOnline() {
    console.log('Conexión restaurada');
    // Opcional: mostrar notificación
    checkServerStatus();
}

/**
 * Maneja cuando la red va offline
 */
function handleNetworkOffline() {
    console.log('Conexión perdida');
    // Opcional: mostrar notificación
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
    // Opcional: implementar indicador visual en la UI
    console.log(`Servidor: ${isOnline ? 'Online' : 'Offline'}`);
}

/**
 * Escapa HTML para prevenir XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

// Exportar funciones principales para uso global
window.handleRunCode = handleRunCode;
window.handleClearOutput = handleClearOutput;
window.handleClearEditor = handleClearEditor;