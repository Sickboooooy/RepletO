"""
🤖 Asistente IA Orquestado - RepletO v2.0

Sistema inteligente que orquesta múltiples IAs para diferentes tareas:
- Autocompletado contextual de código
- Análisis y explicación de errores
- Generación de documentación
- Refactoring automático
- Sugerencias de mejores prácticas
"""

import asyncio
import logging
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import httpx

# Integración con APIs de IA (opcional)
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    anthropic = None

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

logger = logging.getLogger(__name__)

class AIAssistant:
    """
    Orquestador de múltiples servicios de IA para asistencia de código
    """
    
    def __init__(self, 
                 anthropic_api_key: Optional[str] = None,
                 openai_api_key: Optional[str] = None,
                 prefer_local: bool = True):
        """
        Inicializar asistente IA
        
        Args:
            anthropic_api_key: Clave API de Anthropic (Claude)
            openai_api_key: Clave API de OpenAI (GPT)
            prefer_local: Preferir soluciones locales vs APIs externas
        """
        self.prefer_local = prefer_local
        
        # Configurar clientes de IA
        self.anthropic_client = None
        self.openai_client = None
        
        if ANTHROPIC_AVAILABLE and anthropic_api_key:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)
                logger.info("Cliente Anthropic (Claude) configurado")
            except Exception as e:
                logger.warning(f"Error configurando Anthropic: {e}")
        
        if OPENAI_AVAILABLE and openai_api_key:
            try:
                self.openai_client = openai.OpenAI(api_key=openai_api_key)
                logger.info("Cliente OpenAI (GPT) configurado")
            except Exception as e:
                logger.warning(f"Error configurando OpenAI: {e}")
        
        # Patrones para análisis local
        self.syntax_patterns = {
            'python': {
                'common_errors': {
                    r'SyntaxError: invalid syntax': 'Error de sintaxis - verifica paréntesis, comillas y dos puntos',
                    r'IndentationError': 'Error de indentación - usa espacios o tabs consistentemente',
                    r'NameError: name .* is not defined': 'Variable no definida - verifica el nombre y scope',
                    r'TypeError: .* missing .* required positional argument': 'Faltan argumentos en la función',
                    r'AttributeError: .* has no attribute': 'Atributo inexistente - verifica el objeto',
                    r'ImportError|ModuleNotFoundError': 'Módulo no encontrado - verifica la instalación',
                    r'IndexError: .* index out of range': 'Índice fuera de rango - verifica el tamaño de la lista',
                    r'KeyError': 'Clave no encontrada en diccionario - verifica que exista'
                },
                'suggestions': {
                    'print(': '# Para debug, considera usar logging\nimport logging\nlogging.info("mensaje")',
                    'for i in range(len(': '# Mejor: iterar directamente\nfor item in lista:',
                    'try:\n    ': '# Buena práctica: catch específico\nexcept SpecificError as e:',
                    'import *': '# Evita imports masivos\nimport modulo\n# o\nfrom modulo import funcion_especifica'
                }
            },
            'javascript': {
                'common_errors': {
                    r'SyntaxError: Unexpected token': 'Error de sintaxis - verifica llaves, paréntesis y punto y coma',
                    r'ReferenceError: .* is not defined': 'Variable no definida - verifica declaración con let/const/var',
                    r'TypeError: Cannot read property .* of undefined': 'Propiedad de objeto undefined - verifica que exista',
                    r'TypeError: .* is not a function': 'No es una función - verifica el tipo de dato'
                },
                'suggestions': {
                    'var ': '// Mejor: usar let o const\nlet variable = valor;',
                    '== ': '// Mejor: comparación estricta\nif (a === b)',
                    'setTimeout(': '// Considera usar async/await\nasync function delay(ms) {\n  return new Promise(resolve => setTimeout(resolve, ms));\n}'
                }
            }
        }
        
        logger.info("AIAssistant inicializado")

    async def complete_code(self, 
                           code: str, 
                           cursor_position: int,
                           language: str = "python") -> List[Dict[str, Any]]:
        """
        Generar sugerencias de autocompletado
        
        Args:
            code: Código actual
            cursor_position: Posición del cursor
            language: Lenguaje de programación
            
        Returns:
            Lista de sugerencias de autocompletado
        """
        try:
            # Intentar con IA externa primero si está disponible
            if not self.prefer_local and (self.anthropic_client or self.openai_client):
                return await self._ai_complete_code(code, cursor_position, language)
            
            # Fallback: análisis local
            return self._local_complete_code(code, cursor_position, language)
            
        except Exception as e:
            logger.error(f"Error en autocompletado: {e}")
            return self._basic_completions(language)

    def _local_complete_code(self, 
                            code: str, 
                            cursor_position: int,
                            language: str) -> List[Dict[str, Any]]:
        """
        Autocompletado basado en análisis local
        
        Args:
            code: Código actual
            cursor_position: Posición del cursor
            language: Lenguaje de programación
            
        Returns:
            Lista de sugerencias
        """
        suggestions = []
        
        # Obtener contexto alrededor del cursor
        lines = code.split('\n')
        current_line_num = code[:cursor_position].count('\n')
        current_line = lines[current_line_num] if current_line_num < len(lines) else ""
        
        if language == "python":
            suggestions.extend(self._python_completions(code, current_line, cursor_position))
        elif language == "javascript":
            suggestions.extend(self._javascript_completions(code, current_line, cursor_position))
        
        return suggestions[:10]  # Limitar a 10 sugerencias

    def _python_completions(self, code: str, current_line: str, cursor_position: int) -> List[Dict[str, Any]]:
        """Completions específicos para Python"""
        suggestions = []
        
        # Detectar contexto
        if 'import ' in current_line:
            # Sugerir imports comunes
            common_imports = [
                'numpy as np', 'pandas as pd', 'matplotlib.pyplot as plt',
                'os', 'sys', 'json', 'datetime', 'random', 'math'
            ]
            for imp in common_imports:
                if imp not in code:
                    suggestions.append({
                        'label': imp,
                        'insertText': imp,
                        'kind': 'Module',
                        'detail': f'Import {imp.split()[0]}'
                    })
        
        elif current_line.strip().startswith('def '):
            # Sugerir estructura de función
            suggestions.append({
                'label': 'function_template',
                'insertText': '''def function_name(param1, param2):\n    """\n    Descripción de la función\n    \n    Args:\n        param1: Descripción\n        param2: Descripción\n        \n    Returns:\n        Descripción del retorno\n    """\n    pass''',
                'kind': 'Snippet',
                'detail': 'Template de función con docstring'
            })
        
        elif current_line.strip().startswith('class '):
            # Sugerir estructura de clase
            suggestions.append({
                'label': 'class_template',
                'insertText': '''class ClassName:\n    """\n    Descripción de la clase\n    """\n    \n    def __init__(self, param1):\n        self.param1 = param1\n    \n    def method(self):\n        pass''',
                'kind': 'Snippet',
                'detail': 'Template de clase básica'
            })
        
        elif 'print(' in current_line:
            # Sugerir logging en lugar de print
            suggestions.append({
                'label': 'logging_info',
                'insertText': 'logging.info("mensaje")',
                'kind': 'Snippet',
                'detail': 'Usar logging en lugar de print'
            })
        
        elif current_line.strip().endswith(':'):
            # Después de dos puntos, sugerir pass o estructura común
            suggestions.extend([
                {
                    'label': 'pass',
                    'insertText': 'pass',
                    'kind': 'Keyword',
                    'detail': 'Placeholder statement'
                },
                {
                    'label': 'try_except',
                    'insertText': 'try:\n        # código\n    except Exception as e:\n        print(f"Error: {e}")',
                    'kind': 'Snippet',
                    'detail': 'Bloque try-except'
                }
            ])
        
        return suggestions

    def _javascript_completions(self, code: str, current_line: str, cursor_position: int) -> List[Dict[str, Any]]:
        """Completions específicos para JavaScript"""
        suggestions = []
        
        if 'function' in current_line or '=>' in current_line:
            # Sugerir estructura de función
            suggestions.extend([
                {
                    'label': 'async_function',
                    'insertText': 'async function functionName() {\n    // código asíncrono\n}',
                    'kind': 'Snippet',
                    'detail': 'Función asíncrona'
                },
                {
                    'label': 'arrow_function',
                    'insertText': '(param1, param2) => {\n    return result;\n}',
                    'kind': 'Snippet',
                    'detail': 'Arrow function'
                }
            ])
        
        elif 'console.' in current_line:
            # Sugerir métodos de console
            console_methods = ['log', 'error', 'warn', 'info', 'debug', 'table']
            for method in console_methods:
                suggestions.append({
                    'label': f'console.{method}',
                    'insertText': f'console.{method}()',
                    'kind': 'Method',
                    'detail': f'Console {method} method'
                })
        
        return suggestions

    def _basic_completions(self, language: str) -> List[Dict[str, Any]]:
        """Completions básicos cuando todo falla"""
        if language == "python":
            return [
                {'label': 'print', 'insertText': 'print()', 'kind': 'Function', 'detail': 'Print function'},
                {'label': 'len', 'insertText': 'len()', 'kind': 'Function', 'detail': 'Length function'},
                {'label': 'range', 'insertText': 'range()', 'kind': 'Function', 'detail': 'Range function'},
                {'label': 'for', 'insertText': 'for item in iterable:\n    pass', 'kind': 'Snippet', 'detail': 'For loop'},
                {'label': 'if', 'insertText': 'if condition:\n    pass', 'kind': 'Snippet', 'detail': 'If statement'}
            ]
        elif language == "javascript":
            return [
                {'label': 'console.log', 'insertText': 'console.log()', 'kind': 'Function', 'detail': 'Console log'},
                {'label': 'function', 'insertText': 'function name() {\n    \n}', 'kind': 'Snippet', 'detail': 'Function'},
                {'label': 'const', 'insertText': 'const variable = ', 'kind': 'Keyword', 'detail': 'Const declaration'},
                {'label': 'let', 'insertText': 'let variable = ', 'kind': 'Keyword', 'detail': 'Let declaration'}
            ]
        
        return []

    async def _ai_complete_code(self, 
                               code: str, 
                               cursor_position: int,
                               language: str) -> List[Dict[str, Any]]:
        """
        Autocompletado usando IA externa
        
        Args:
            code: Código actual
            cursor_position: Posición del cursor
            language: Lenguaje de programación
            
        Returns:
            Lista de sugerencias de IA
        """
        try:
            # Preparar contexto para la IA
            before_cursor = code[:cursor_position]
            after_cursor = code[cursor_position:]
            
            prompt = f"""Proporciona 5 sugerencias de autocompletado para este código {language}:

CÓDIGO ANTES DEL CURSOR:
{before_cursor}

CÓDIGO DESPUÉS DEL CURSOR:
{after_cursor}

Responde en formato JSON con esta estructura:
[
  {{
    "label": "nombre_sugerencia",
    "insertText": "código_a_insertar",
    "kind": "Function|Variable|Snippet|Keyword",
    "detail": "descripción_breve"
  }}
]

Enfócate en:
1. Contexto inmediato del cursor
2. Mejores prácticas del lenguaje
3. Patrones comunes y útiles
4. Corrección de errores potenciales
"""
            
            if self.anthropic_client:
                response = await self._call_anthropic(prompt)
            elif self.openai_client:
                response = await self._call_openai(prompt)
            else:
                return self._local_complete_code(code, cursor_position, language)
            
            # Parsear respuesta JSON
            suggestions = json.loads(response)
            return suggestions[:5]  # Limitar a 5 sugerencias
            
        except Exception as e:
            logger.error(f"Error en AI completion: {e}")
            return self._local_complete_code(code, cursor_position, language)

    async def explain_error(self, 
                           code: str, 
                           error: str,
                           language: str = "python") -> Dict[str, Any]:
        """
        Analizar y explicar errores de código
        
        Args:
            code: Código que causó el error
            error: Mensaje de error
            language: Lenguaje de programación
            
        Returns:
            Explicación detallada del error y sugerencias
        """
        try:
            # Intentar análisis local primero
            local_explanation = self._analyze_error_locally(error, language)
            
            if local_explanation and self.prefer_local:
                return local_explanation
            
            # Si no hay explicación local o preferimos IA externa
            if self.anthropic_client or self.openai_client:
                ai_explanation = await self._ai_explain_error(code, error, language)
                # Combinar análisis local y IA
                if local_explanation:
                    ai_explanation['local_analysis'] = local_explanation
                return ai_explanation
            
            return local_explanation or self._generic_error_explanation(error)
            
        except Exception as e:
            logger.error(f"Error explicando error: {e}")
            return self._generic_error_explanation(error)

    def _analyze_error_locally(self, error: str, language: str) -> Optional[Dict[str, Any]]:
        """Análisis local de errores usando patrones conocidos"""
        if language not in self.syntax_patterns:
            return None
        
        patterns = self.syntax_patterns[language]['common_errors']
        
        for pattern, explanation in patterns.items():
            if re.search(pattern, error, re.IGNORECASE):
                return {
                    'summary': 'Error común detectado',
                    'explanation': explanation,
                    'error_type': pattern.split(':')[0] if ':' in pattern else 'RuntimeError',
                    'confidence': 'high',
                    'suggestions': [
                        'Revisa la línea indicada en el error',
                        'Verifica la sintaxis del lenguaje',
                        'Consulta la documentación si es necesario'
                    ]
                }
        
        return None

    async def _ai_explain_error(self, 
                               code: str, 
                               error: str,
                               language: str) -> Dict[str, Any]:
        """Explicación de errores usando IA externa"""
        prompt = f"""Analiza este error de código {language} y proporciona una explicación detallada:

CÓDIGO:
```{language}
{code}
```

ERROR:
{error}

Responde en formato JSON:
{{
  "summary": "resumen_breve_del_error",
  "explanation": "explicación_detallada",
  "error_type": "tipo_de_error",
  "line_number": número_de_línea_problema,
  "suggestions": [
    "sugerencia_1",
    "sugerencia_2",
    "sugerencia_3"
  ],
  "fixed_code": "código_corregido_si_es_posible",
  "confidence": "low|medium|high"
}}

Enfócate en:
1. Explicación clara para desarrolladores
2. Soluciones prácticas y específicas
3. Mejores prácticas del lenguaje
4. Prevención de errores similares
"""
        
        try:
            if self.anthropic_client:
                response = await self._call_anthropic(prompt)
            elif self.openai_client:
                response = await self._call_openai(prompt)
            else:
                return self._generic_error_explanation(error)
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Error en AI error explanation: {e}")
            return self._generic_error_explanation(error)

    def _generic_error_explanation(self, error: str) -> Dict[str, Any]:
        """Explicación genérica cuando no hay otra opción"""
        return {
            'summary': 'Error detectado en el código',
            'explanation': 'Se ha producido un error durante la ejecución. Revisa el mensaje de error para más detalles.',
            'error_type': 'Unknown',
            'suggestions': [
                'Lee cuidadosamente el mensaje de error',
                'Verifica la sintaxis del código',
                'Revisa la documentación del lenguaje',
                'Busca ejemplos similares online'
            ],
            'confidence': 'low',
            'error_message': error
        }

    async def _call_anthropic(self, prompt: str) -> str:
        """Llamar a la API de Anthropic (Claude)"""
        try:
            response = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Error llamando Anthropic: {e}")
            raise

    async def _call_openai(self, prompt: str) -> str:
        """Llamar a la API de OpenAI (GPT)"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error llamando OpenAI: {e}")
            raise

    async def generate_documentation(self, code: str, language: str = "python") -> str:
        """
        Generar documentación automática para código
        
        Args:
            code: Código a documentar
            language: Lenguaje de programación
            
        Returns:
            Documentación generada
        """
        if language == "python":
            return self._generate_python_docs(code)
        elif language == "javascript":
            return self._generate_js_docs(code)
        
        return f"# Documentación\n\nCódigo en {language}:\n\n```{language}\n{code}\n```"

    def _generate_python_docs(self, code: str) -> str:
        """Generar documentación para Python"""
        lines = code.split('\n')
        documented_lines = []
        
        for line in lines:
            documented_lines.append(line)
            
            # Detectar definiciones de función sin docstring
            if line.strip().startswith('def ') and ':' in line:
                # Verificar si la siguiente línea no es un docstring
                func_name = line.split('def ')[1].split('(')[0]
                docstring = f'    """\n    Descripción de la función {func_name}\n    \n    Returns:\n        Descripción del valor de retorno\n    """\n'
                documented_lines.append(docstring)
        
        return '\n'.join(documented_lines)

    def _generate_js_docs(self, code: str) -> str:
        """Generar documentación para JavaScript"""
        lines = code.split('\n')
        documented_lines = []
        
        for line in lines:
            documented_lines.append(line)
            
            # Detectar funciones sin JSDoc
            if ('function ' in line or '=>' in line) and '{' in line:
                func_name = 'function'
                if 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0].strip()
                
                jsdoc = f"""/**
 * Descripción de la función {func_name}
 * @param {{any}} param - Descripción del parámetro
 * @returns {{any}} Descripción del retorno
 */"""
                documented_lines.insert(-1, jsdoc)
        
        return '\n'.join(documented_lines)