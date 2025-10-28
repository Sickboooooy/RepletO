// RepletO - Editor Management
// Configuración y manejo del Monaco Editor

let editor = null;
let isEditorReady = false;
let editorInitTimeout = null;

// Configuración del Monaco Editor
const EDITOR_CONFIG = {
    theme: 'vs-dark',
    language: 'python',
    fontSize: 14,
    fontFamily: "'Fira Code', 'Cascadia Code', 'Monaco', 'Menlo', monospace",
    lineNumbers: 'on',
    minimap: { enabled: false },
    automaticLayout: true,
    tabSize: 4,
    insertSpaces: true,
    wordWrap: 'on',
    scrollBeyondLastLine: false,
    renderLineHighlight: 'line',
    selectionHighlight: true,
    bracketPairColorization: { enabled: true },
    folding: true,
    showFoldingControls: 'always',
    smoothScrolling: true,
    cursorBlinking: 'smooth',
    cursorSmoothCaretAnimation: true,
    contextmenu: true,
    mouseWheelZoom: true,
    quickSuggestions: {
        other: true,
        comments: false,
        strings: false
    },
    parameterHints: { enabled: true },
    autoIndent: 'full',
    formatOnPaste: true,
    formatOnType: true
};

// Código de ejemplo inicial
const INITIAL_CODE = `# ¡Bienvenido a RepletO!
# Tu editor de Python online

print("¡Hola RepletO!")

# Prueba con variables
nombre = "Desarrollador"
print(f"Bienvenido, {nombre}!")

# Ejemplo de bucle
print("\\nContando del 1 al 5:")
for i in range(1, 6):
    print(f"  Número: {i}")

# Ejemplo de función
def calcular_cuadrado(numero):
    return numero ** 2

resultado = calcular_cuadrado(8)
print(f"\\nEl cuadrado de 8 es: {resultado}")

# Ejemplo de lista
frutas = ["manzana", "banana", "naranja"]
print("\\nFrutas disponibles:")
for i, fruta in enumerate(frutas, 1):
    print(f"  {i}. {fruta.title()}")

print("\\n¡Listo para programar!")`;

/**
 * Inicializa el Monaco Editor con fallback
 */
async function initializeEditor() {
    console.log('🔧 Iniciando Monaco Editor...');
    
    try {
        // Mostrar indicador de carga
        showEditorLoading();

        // Limpiar timeout anterior si existe
        if (editorInitTimeout) {
            clearTimeout(editorInitTimeout);
        }

        // Timeout de seguridad de 5 segundos para Monaco
        editorInitTimeout = setTimeout(() => {
            console.error('❌ Timeout cargando Monaco Editor');
            initializeFallbackEditor();
        }, 5000);

        // Esperar a que Monaco se cargue o timeout
        if (typeof window.monacoLoaded === 'undefined') {
            // Esperar un poco más por Monaco
            await new Promise(resolve => setTimeout(resolve, 2000));
        }

        // Verificar si Monaco se cargó
        if (window.monacoLoaded === false || typeof require === 'undefined') {
            console.warn('⚠️ Monaco no disponible, usando editor de fallback');
            clearTimeout(editorInitTimeout);
            initializeFallbackEditor();
            return;
        }

        // Intentar cargar Monaco
        if (typeof require !== 'undefined' && require.config) {
            require.config({ 
                paths: { 
                    'vs': 'https://unpkg.com/monaco-editor@0.44.0/min/vs'
                },
                timeout: 3000
            });

            require(['vs/editor/editor.main'], 
                function() {
                    clearTimeout(editorInitTimeout);
                    createMonacoEditor();
                },
                function(error) {
                    console.warn('⚠️ Error cargando Monaco:', error);
                    clearTimeout(editorInitTimeout);
                    initializeFallbackEditor();
                }
            );
        } else {
            // require no disponible, usar fallback
            clearTimeout(editorInitTimeout);
            initializeFallbackEditor();
        }

    } catch (error) {
        console.error('❌ Error inicializando editor:', error);
        clearTimeout(editorInitTimeout);
        initializeFallbackEditor();
    }
}

/**
 * Crea la instancia del Monaco Editor
 */
function createMonacoEditor() {
    try {
        console.log('✅ Monaco Editor cargado, creando instancia...');
        
        const editorContainer = document.getElementById('editor');
        
        if (!editorContainer) {
            throw new Error('Contenedor del editor no encontrado');
        }

        // Limpiar contenedor
        editorContainer.innerHTML = '';

        // Crear instancia del editor
        editor = monaco.editor.create(editorContainer, {
            value: INITIAL_CODE,
            ...EDITOR_CONFIG
        });

        // Configurar eventos del editor
        setupEditorEvents();

        // Configurar temas personalizados
        setupCustomThemes();

        // Marcar como listo
        isEditorReady = true;
        hideEditorLoading();

        console.log('✅ Monaco Editor inicializado correctamente');

        // Disparar evento personalizado
        window.dispatchEvent(new CustomEvent('editorReady', { 
            detail: { editor } 
        }));

        // Focus inicial en el editor
        setTimeout(() => {
            editor.focus();
        }, 100);

    } catch (error) {
        console.error('❌ Error creando Monaco Editor:', error);
        initializeFallbackEditor();
    }
}

/**
 * Inicializa editor de fallback (textarea simple)
 */
function initializeFallbackEditor() {
    console.log('🔄 Iniciando editor de fallback...');
    
    try {
        const editorContainer = document.getElementById('editor');
        
        if (!editorContainer) {
            console.error('❌ Contenedor del editor no encontrado');
            return;
        }

        // Crear textarea de fallback
        editorContainer.innerHTML = `
            <textarea 
                id="fallback-editor" 
                class="fallback-editor"
                placeholder="# Editor de fallback - Monaco no disponible
# Escribe tu código Python aquí...

print('¡Hola RepletO!')"
                spellcheck="false"
            >${INITIAL_CODE}</textarea>
        `;

        const textarea = editorContainer.querySelector('#fallback-editor');
        
        if (textarea) {
            // Simular API de Monaco
            editor = {
                getValue: () => textarea.value,
                setValue: (value) => { textarea.value = value; },
                focus: () => textarea.focus(),
                getPosition: () => ({ lineNumber: 1, column: 1 }),
                getSelection: () => null,
                layout: () => {}
            };

            // Configurar eventos básicos
            textarea.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    e.preventDefault();
                    window.dispatchEvent(new CustomEvent('runCode'));
                }
                
                if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
                    e.preventDefault();
                    window.dispatchEvent(new CustomEvent('clearOutput'));
                }
            });

            isEditorReady = true;
            hideEditorLoading();

            console.log('✅ Editor de fallback inicializado');

            // Disparar evento personalizado
            window.dispatchEvent(new CustomEvent('editorReady', { 
                detail: { editor, fallback: true } 
            }));

            textarea.focus();
        }

    } catch (error) {
        console.error('❌ Error inicializando editor de fallback:', error);
        showEditorError('No se pudo inicializar ningún editor');
    }
}

/**
 * Configura eventos del editor
 */
function setupEditorEvents() {
    if (!editor) return;

    // Evento de cambio de contenido
    editor.onDidChangeModelContent(() => {
        // Opcional: guardar en localStorage
        saveEditorContent();
    });

    // Evento de cambio de selección
    editor.onDidChangeCursorSelection(() => {
        // Opcional: mostrar información de línea/columna
        updateCursorInfo();
    });

    // Shortcuts personalizados
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
        // Ejecutar código con Ctrl+Enter
        window.dispatchEvent(new CustomEvent('runCode'));
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyL, () => {
        // Limpiar output con Ctrl+L
        window.dispatchEvent(new CustomEvent('clearOutput'));
    });

    // Prevenir Ctrl+S (guardar navegador)
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
        // Opcional: implementar guardado personalizado
        console.log('Guardado personalizado (Ctrl+S interceptado)');
    });
}

/**
 * Configura temas personalizados
 */
function setupCustomThemes() {
    // Tema personalizado RepletO
    monaco.editor.defineTheme('repleto-dark', {
        base: 'vs-dark',
        inherit: true,
        rules: [
            { token: 'comment', foreground: '6A9955', fontStyle: 'italic' },
            { token: 'keyword', foreground: '569CD6', fontStyle: 'bold' },
            { token: 'string', foreground: 'CE9178' },
            { token: 'number', foreground: 'B5CEA8' },
            { token: 'regexp', foreground: 'D16969' },
            { token: 'operator', foreground: 'D4D4D4' },
            { token: 'namespace', foreground: '4EC9B0' },
            { token: 'type', foreground: '4EC9B0' },
            { token: 'struct', foreground: '4EC9B0' },
            { token: 'class', foreground: '4EC9B0' },
            { token: 'interface', foreground: '4EC9B0' },
            { token: 'parameter', foreground: '9CDCFE' },
            { token: 'variable', foreground: '9CDCFE' },
            { token: 'function', foreground: 'DCDCAA' },
            { token: 'member', foreground: 'DCDCAA' }
        ],
        colors: {
            'editor.background': '#1e1e1e',
            'editor.foreground': '#d4d4d4',
            'editorLineNumber.foreground': '#6e7681',
            'editorLineNumber.activeForeground': '#cccccc',
            'editor.selectionBackground': '#264f78',
            'editor.inactiveSelectionBackground': '#3a3d41',
            'editorCursor.foreground': '#aeafad',
            'editor.lineHighlightBackground': '#2d2d30',
            'editorWhitespace.foreground': '#404040',
            'editorIndentGuide.background': '#404040',
            'editorIndentGuide.activeBackground': '#707070'
        }
    });

    // Aplicar tema personalizado
    monaco.editor.setTheme('repleto-dark');
}

/**
 * Configura autocompletado personalizado
 */
function setupCustomCompletion() {
    // Registrar proveedor de autocompletado para Python
    monaco.languages.registerCompletionItemProvider('python', {
        provideCompletionItems: (model, position) => {
            const suggestions = [
                {
                    label: 'print_hello',
                    kind: monaco.languages.CompletionItemKind.Snippet,
                    documentation: 'Imprimir saludo',
                    insertText: 'print("¡Hola RepletO!")',
                    range: {
                        startLineNumber: position.lineNumber,
                        endLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endColumn: position.column
                    }
                },
                {
                    label: 'for_loop',
                    kind: monaco.languages.CompletionItemKind.Snippet,
                    documentation: 'Bucle for básico',
                    insertText: [
                        'for ${1:i} in range(${2:10}):',
                        '    ${0:pass}'
                    ].join('\n'),
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    range: {
                        startLineNumber: position.lineNumber,
                        endLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endColumn: position.column
                    }
                },
                {
                    label: 'function_def',
                    kind: monaco.languages.CompletionItemKind.Snippet,
                    documentation: 'Definición de función',
                    insertText: [
                        'def ${1:function_name}(${2:parameters}):',
                        '    """${3:Descripción de la función}"""',
                        '    ${0:pass}'
                    ].join('\n'),
                    insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                    range: {
                        startLineNumber: position.lineNumber,
                        endLineNumber: position.lineNumber,
                        startColumn: position.column,
                        endColumn: position.column
                    }
                }
            ];

            return { suggestions };
        }
    });
}

/**
 * Obtiene el código actual del editor
 * @returns {string} Código del editor
 */
function getEditorValue() {
    if (!editor || !isEditorReady) {
        console.warn('Editor no está listo');
        return '';
    }
    return editor.getValue();
}

/**
 * Establece el código en el editor
 * @param {string} code - Código a establecer
 */
function setEditorValue(code) {
    if (!editor || !isEditorReady) {
        console.warn('Editor no está listo');
        return;
    }
    editor.setValue(code);
}

/**
 * Limpia el contenido del editor
 */
function clearEditor() {
    setEditorValue('');
}

/**
 * Redimensiona el editor
 */
function resizeEditor() {
    if (editor && isEditorReady) {
        editor.layout();
    }
}

/**
 * Guarda el contenido del editor en localStorage
 */
function saveEditorContent() {
    if (!editor || !isEditorReady) return;
    
    try {
        const content = editor.getValue();
        localStorage.setItem('repleto-editor-content', content);
    } catch (error) {
        console.warn('No se pudo guardar en localStorage:', error);
    }
}

/**
 * Carga el contenido del editor desde localStorage
 */
function loadEditorContent() {
    try {
        const saved = localStorage.getItem('repleto-editor-content');
        if (saved && saved.trim()) {
            return saved;
        }
    } catch (error) {
        console.warn('No se pudo cargar desde localStorage:', error);
    }
    return INITIAL_CODE;
}

/**
 * Actualiza información del cursor
 */
function updateCursorInfo() {
    if (!editor) return;
    
    const position = editor.getPosition();
    const selection = editor.getSelection();
    
    // Opcional: mostrar información en la UI
    console.debug(`Línea: ${position.lineNumber}, Columna: ${position.column}`);
}

/**
 * Muestra indicador de carga del editor
 */
function showEditorLoading() {
    const container = document.getElementById('editor');
    if (container) {
        container.innerHTML = `
            <div class="editor-loading">
                <div class="loading-text">
                    <span>⚙️</span>
                    Cargando editor<span class="loading-dots"></span>
                </div>
            </div>
        `;
    }
}

/**
 * Oculta indicador de carga del editor
 */
function hideEditorLoading() {
    // El editor se carga automáticamente en el contenedor
}

/**
 * Muestra error del editor
 */
function showEditorError(message) {
    const container = document.getElementById('editor');
    if (container) {
        container.innerHTML = `
            <div class="editor-loading">
                <div class="loading-text" style="color: var(--error-color);">
                    <span>❌</span>
                    Error cargando editor: ${message}
                </div>
            </div>
        `;
    }
}

// Inicializar editor cuando se carga el DOM
document.addEventListener('DOMContentLoaded', () => {
    initializeEditor();
});

// Redimensionar editor cuando cambia el tamaño de ventana
window.addEventListener('resize', () => {
    setTimeout(resizeEditor, 100);
});

// Exportar funciones globales
window.getEditorValue = getEditorValue;
window.setEditorValue = setEditorValue;
window.clearEditor = clearEditor;
window.resizeEditor = resizeEditor;