"""
Detector de errores ortográficos usando LanguageTool.
Integración mejorada con filtros para español.
"""
import language_tool_python
from typing import List, Tuple
import re


class SpellingChecker:
    """Detector de errores ortográficos con LanguageTool."""
    
    def __init__(self):
        """Inicializa LanguageTool para español."""
        self.tool = None
        self.habilitado = False
        
        try:
            print("⏳ Inicializando LanguageTool (puede tardar 10-20 segundos)...")
            self.tool = language_tool_python.LanguageTool('es')
            self.habilitado = True
            print("✓ LanguageTool listo")
        except Exception as e:
            print(f"⚠️ LanguageTool no disponible: {e}")
            print("   Las detecciones ortográficas estarán deshabilitadas")
    
    def detectar_errores(self, texto: str, max_errores: int = 50) -> List[Tuple[str, str, str]]:
        """
        Detecta errores ortográficos en el texto.
        
        Args:
            texto: Texto a analizar
            max_errores: Máximo número de errores a retornar
            
        Returns:
            Lista de (fragmento_error, corrección, explicación)
        """
        if not self.habilitado or not texto.strip():
            return []
        
        try:
            # Limitar longitud (LanguageTool tiene límite)
            if len(texto) > 10000:
                texto = texto[:10000]
            
            # Detectar errores
            matches = self.tool.check(texto)
            
            resultados = []
            for match in matches[:max_errores]:
                # Filtrar solo errores ortográficos relevantes
                if self._es_error_relevante(match):
                    error_text = texto[match.offset:match.offset + match.errorLength]
                    
                    # Obtener primera corrección sugerida
                    if match.replacements:
                        correccion = match.replacements[0]
                        explicacion = match.message[:100]  # Truncar explicación
                        
                        resultados.append((
                            error_text,
                            correccion,
                            f"Ortografía: {explicacion}"
                        ))
            
            return resultados
            
        except Exception as e:
            print(f"⚠️ Error en LanguageTool: {e}")
            return []
    
    def _es_error_relevante(self, match) -> bool:
        """
        Filtra errores relevantes (ortografía, no estilo).
        
        Args:
            match: Match de LanguageTool
            
        Returns:
            True si es error relevante
        """
        # Categorías relevantes
        categorias_relevantes = [
            'TYPOS',           # Errores tipográficos
            'MISSPELLING',     # Palabras mal escritas
            'MORFOLOGIK',      # Errores ortográficos del diccionario
            'ORTOGRAFIA',      # Ortografía general
        ]
        
        # Reglas a excluir (estilo, no ortografía)
        reglas_excluidas = [
            'WHITESPACE',      # Espacios
            'PUNTUACION',      # Puntuación (ya lo manejamos)
            'MAYUSCULAS',      # Mayúsculas (pueden ser nombres propios)
            'PASSIVE_VOICE',   # Voz pasiva (se maneja aparte)
        ]
        
        # Verificar categoría
        if match.category:
            for cat in categorias_relevantes:
                if cat.lower() in match.category.lower():
                    return True
        
        # Verificar que no esté en excluidas
        if match.ruleId:
            for excluida in reglas_excluidas:
                if excluida.lower() in match.ruleId.lower():
                    return False
        
        # Si tiene mensaje de "ortografía" o "palabra"
        if match.message:
            msg_lower = match.message.lower()
            if 'ortografía' in msg_lower or 'palabra' in msg_lower or 'escrito' in msg_lower:
                return True
        
        return False
    
    def cerrar(self):
        """Cierra LanguageTool."""
        if self.tool:
            try:
                self.tool.close()
            except:
                pass


if __name__ == '__main__':
    # Test
    checker = SpellingChecker()
    
    if checker.habilitado:
        texto_test = """
        Este es un texto para probar. La palabra pertenneció está mal escrita.
        También carintios debería ser corintios.
        """
        
        errores = checker.detectar_errores(texto_test)
        
        print(f"\n📊 Detectados {len(errores)} errores ortográficos:\n")
        for error, corr, expl in errores:
            print(f"  ✗ '{error}' → '{corr}'")
            print(f"    {expl}\n")
    
    checker.cerrar()
