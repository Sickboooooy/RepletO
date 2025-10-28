// 🌐 RepletO v2.0 - API Client Avanzado
// ====================================
// Cliente WebSocket + REST API con funcionalidades avanzadas

const API_BASE_URL = 'http://127.0.0.1:8000';
const WS_BASE_URL = 'ws://127.0.0.1:8000';
const API_TIMEOUT = 30000; // 30 segundos

class RepletOAPI {
    constructor() {
        this.baseURL = API_BASE_URL;
        this.wsBaseURL = WS_BASE_URL;
        this.timeout = API_TIMEOUT;
        this.sessionId = this.generateSessionId();
        this.wsConnection = null;
        this.wsReconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        
        // Callbacks para eventos WebSocket
        this.callbacks = {
            output: [],
            error: [],
            completion: [],
            disconnect: [],
            ai_suggestion: []
        };
        
        this.initializeWebSocket();
    }

    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }

    /**
     * 🔌 Inicializar conexión WebSocket
     */
    initializeWebSocket() {
        try {
            this.wsConnection = new WebSocket(`${this.wsBaseURL}/ws/${this.sessionId}`);
            
            this.wsConnection.onopen = () => {
                console.log('🟢 WebSocket conectado');
                this.wsReconnectAttempts = 0;
                this.emit('connect', { sessionId: this.sessionId });
            };
            
            this.wsConnection.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.wsConnection.onclose = () => {
                console.log('🔴 WebSocket desconectado');
                this.emit('disconnect');
                this.attemptReconnect();
            };
            
            this.wsConnection.onerror = (error) => {
                console.error('🚨 WebSocket error:', error);
                this.emit('error', { error: 'WebSocket connection error' });
            };
            
        } catch (error) {
            console.error('Error inicializando WebSocket:', error);
        }
    }

    /**
     * 🔄 Intento de reconexión WebSocket
     */
    attemptReconnect() {
        if (this.wsReconnectAttempts < this.maxReconnectAttempts) {
            this.wsReconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.wsReconnectAttempts - 1);
            
            console.log(`🔄 Reintentando conexión WebSocket (${this.wsReconnectAttempts}/${this.maxReconnectAttempts}) en ${delay}ms`);
            
            setTimeout(() => {
                this.initializeWebSocket();
            }, delay);
        } else {
            console.error('🚨 Máximo número de intentos de reconexión alcanzado');
            this.emit('max_reconnect_reached');
        }
    }

    /**
     * 📨 Manejar mensajes WebSocket
     */
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'output':
                this.emit('output', data);
                break;
            case 'error':
                this.emit('error', data);
                break;
            case 'execution_complete':
                this.emit('completion', data);
                break;
            case 'ai_suggestion':
                this.emit('ai_suggestion', data);
                break;
            case 'ping':
                this.sendWebSocketMessage({ type: 'pong' });
                break;
            default:
                console.log('WebSocket mensaje no manejado:', data);
        }
    }

    /**
     * 📤 Enviar mensaje por WebSocket
     */
    sendWebSocketMessage(message) {
        if (this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN) {
            this.wsConnection.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket no está conectado');
        }
    }

    /**
     * 👂 Registrar callback para eventos
     */
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }

    /**
     * 🚫 Remover callback de eventos
     */
    off(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event] = this.callbacks[event].filter(cb => cb !== callback);
        }
    }

    /**
     * 📢 Emitir evento
     */
    emit(event, data = {}) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error en callback ${event}:`, error);
                }
            });
        }
    }

    /**
     * 🌐 Petición HTTP con manejo avanzado
     */
    async request(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const fullURL = url.startsWith('http') ? url : `${this.baseURL}${url}`;
            
            const response = await fetch(fullURL, {
                ...options,
                signal: controller.signal,
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-ID': this.sessionId,
                    ...options.headers
                }
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('⏱️ La petición ha excedido el tiempo límite');
            }
            
            if (error.message.includes('Failed to fetch')) {
                throw new Error('🔌 No se puede conectar con el servidor RepletO');
            }
            
            throw error;
        }
    }

    /**
     * 🐍 Ejecutar código con streaming en tiempo real
     */
    async executeCodeStreaming(code, language = 'python') {
        if (!code || !code.trim()) {
            this.emit('error', { error: 'No se proporcionó código para ejecutar' });
            return;
        }

        this.sendWebSocketMessage({
            type: 'execute_code',
            data: {
                code: code.trim(),
                language: language,
                session_id: this.sessionId
            }
        });
    }

    /**
     * 🐍 Ejecutar código tradicional (REST API)
     */
    async executeCode(code, language = 'python') {
        if (!code || !code.trim()) {
            return {
                status: 'error',
                output: '',
                error: 'No se proporcionó código para ejecutar'
            };
        }

        try {
            const response = await this.request('/execute', {
                method: 'POST',
                body: JSON.stringify({
                    code: code.trim(),
                    language: language,
                    session_id: this.sessionId
                })
            });

            const result = await response.json();
            
            return {
                status: result.status,
                output: result.output || '',
                error: result.error || null,
                execution_time: result.execution_time,
                memory_used: result.memory_used,
                timestamp: new Date().toISOString()
            };

        } catch (error) {
            console.error('❌ Error ejecutando código:', error);
            
            return {
                status: 'error',
                output: '',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * 🤖 Obtener sugerencias de autocompletado IA
     */
    async getCodeCompletion(code, cursorPosition, language = 'python') {
        try {
            const response = await this.request('/ai/complete', {
                method: 'POST',
                body: JSON.stringify({
                    code: code,
                    cursor_position: cursorPosition,
                    language: language,
                    session_id: this.sessionId
                })
            });

            const result = await response.json();
            return result.suggestions || [];

        } catch (error) {
            console.error('❌ Error obteniendo completions:', error);
            return [];
        }
    }

    /**
     * 🔍 Explicar error con IA
     */
    async explainError(code, error, language = 'python') {
        try {
            const response = await this.request('/ai/explain-error', {
                method: 'POST',
                body: JSON.stringify({
                    code: code,
                    error: error,
                    language: language
                })
            });

            const result = await response.json();
            return result;

        } catch (error) {
            console.error('❌ Error explicando error:', error);
            return {
                summary: 'Error en la explicación',
                explanation: 'No se pudo obtener explicación del error',
                suggestions: ['Revisa la sintaxis del código']
            };
        }
    }

    /**
     * 📚 Gestión de snippets
     */
    async saveSnippet(title, code, language, description = '', tags = []) {
        try {
            const response = await this.request('/snippets', {
                method: 'POST',
                body: JSON.stringify({
                    title: title,
                    code: code,
                    language: language,
                    description: description,
                    tags: tags
                })
            });

            return await response.json();
        } catch (error) {
            console.error('❌ Error guardando snippet:', error);
            throw error;
        }
    }

    async searchSnippets(query = '', language = '', tags = []) {
        try {
            const params = new URLSearchParams();
            if (query) params.append('q', query);
            if (language) params.append('language', language);
            if (tags.length > 0) params.append('tags', tags.join(','));

            const response = await this.request(`/snippets/search?${params}`);
            return await response.json();
        } catch (error) {
            console.error('❌ Error buscando snippets:', error);
            return [];
        }
    }

    /**
     * 📊 Historial de ejecuciones
     */
    async getExecutionHistory(limit = 50) {
        try {
            const response = await this.request(`/history?limit=${limit}&session_id=${this.sessionId}`);
            return await response.json();
        } catch (error) {
            console.error('❌ Error obteniendo historial:', error);
            return [];
        }
    }

    /**
     * 🔄 Sincronización Git
     */
    async gitStatus() {
        try {
            const response = await this.request('/git/status');
            return await response.json();
        } catch (error) {
            console.error('❌ Error obteniendo estado Git:', error);
            return { status: 'error', message: error.message };
        }
    }

    async gitCommit(message = null) {
        try {
            const response = await this.request('/git/commit', {
                method: 'POST',
                body: JSON.stringify({ message: message })
            });
            return await response.json();
        } catch (error) {
            console.error('❌ Error en Git commit:', error);
            return { status: 'error', message: error.message };
        }
    }

    async gitPush() {
        try {
            const response = await this.request('/git/push', {
                method: 'POST'
            });
            return await response.json();
        } catch (error) {
            console.error('❌ Error en Git push:', error);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * 🔧 Jupyter Kernel
     */
    async createJupyterSession(language = 'python') {
        try {
            const response = await this.request('/jupyter/session', {
                method: 'POST',
                body: JSON.stringify({
                    language: language,
                    session_id: this.sessionId
                })
            });
            return await response.json();
        } catch (error) {
            console.error('❌ Error creando sesión Jupyter:', error);
            return { status: 'error', message: error.message };
        }
    }

    /**
     * ❤️ Health check
     */
    async checkHealth() {
        try {
            const response = await this.request('/health');
            const result = await response.json();
            
            return {
                status: 'online',
                data: result,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('❌ Error verificando salud del servidor:', error);
            
            return {
                status: 'offline',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * 📋 Información del servidor
     */
    async getServerInfo() {
        try {
            const response = await this.request('/');
            const result = await response.json();
            
            return {
                status: 'success',
                data: result,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            console.error('❌ Error obteniendo información del servidor:', error);
            
            return {
                status: 'error',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }

    /**
     * 💾 Configuraciones
     */
    async saveSetting(key, value) {
        try {
            const response = await this.request('/settings', {
                method: 'POST',
                body: JSON.stringify({ key: key, value: value })
            });
            return await response.json();
        } catch (error) {
            console.error('❌ Error guardando configuración:', error);
            throw error;
        }
    }

    async getSetting(key, defaultValue = null) {
        try {
            const response = await this.request(`/settings/${key}`);
            const result = await response.json();
            return result.value !== undefined ? result.value : defaultValue;
        } catch (error) {
            console.error('❌ Error obteniendo configuración:', error);
            return defaultValue;
        }
    }

    /**
     * 🧹 Cleanup
     */
    disconnect() {
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }
    }
}

// 🌍 Instancia global
const repletOAPI = new RepletOAPI();

// 🔧 Funciones de conveniencia
window.executeCode = (code, language) => repletOAPI.executeCode(code, language);
window.executeCodeStreaming = (code, language) => repletOAPI.executeCodeStreaming(code, language);
window.getCodeCompletion = (code, pos, lang) => repletOAPI.getCodeCompletion(code, pos, lang);
window.explainError = (code, error, lang) => repletOAPI.explainError(code, error, lang);
window.checkHealth = () => repletOAPI.checkHealth();
window.getServerInfo = () => repletOAPI.getServerInfo();

// 🛠️ Utilidades
function formatError(error) {
    if (typeof error === 'string') return error;
    if (error && error.message) return error.message;
    return 'Error desconocido';
}

function getErrorType(error) {
    const errorStr = error.toString().toLowerCase();
    
    if (errorStr.includes('timeout') || errorStr.includes('tiempo')) return 'timeout';
    if (errorStr.includes('network') || errorStr.includes('fetch') || errorStr.includes('conectar')) return 'network';
    if (errorStr.includes('syntax') || errorStr.includes('sintaxis')) return 'syntax';
    if (errorStr.includes('permission') || errorStr.includes('prohibida')) return 'security';
    
    return 'runtime';
}

// 🚀 Inicialización
document.addEventListener('DOMContentLoaded', async () => {
    try {
        console.log('🚀 RepletO v2.0 API Cliente inicializado');
        const health = await repletOAPI.checkHealth();
        console.log('📊 Estado del servidor:', health);
        
        if (health.status === 'offline') {
            console.warn('⚠️ El servidor backend no está respondiendo');
        }
    } catch (error) {
        console.error('❌ Error verificando servidor inicial:', error);
    }
});

// 🧹 Cleanup al cerrar ventana
window.addEventListener('beforeunload', () => {
    repletOAPI.disconnect();
});

// 📤 Exportar para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RepletOAPI, repletOAPI, formatError, getErrorType };
}