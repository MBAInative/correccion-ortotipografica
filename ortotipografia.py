"""
Reglas deterministas de ortotipografía para español.
Basado en normativa RAE, ASALE y José Martínez de Sousa.
"""
import re
from typing import List, Tuple


class OrtotipografiaRules:
    """Reglas de corrección ortotipográfica deterministas."""
    
    # Definición de caracteres especiales
    COMILLA_LATINA_ABRE = '«'
    COMILLA_LATINA_CIERRA = '»'
    COMILLA_INGLESA_ABRE = '"'
    COMILLA_INGLESA_CIERRA = '"'
    COMILLA_SIMPLE_ABRE = '''
    COMILLA_SIMPLE_CIERRA = '''
    RAYA = '—'  # U+2014 (em-dash)
    GUION = '-'  # U+002D (hyphen)
    ESPACIO_DURO = '\u00A0'  # Non-breaking space
    
    def __init__(self):
        """Inicializa las reglas de ortotipografía."""
        pass
    
    def corregir_comillas(self, texto: str) -> str:
        """
        Convierte comillas inglesas a latinas según jerarquía RAE.
        
        Jerarquía:
        1. Primarias: « »
        2. Secundarias: " "
        3. Terciarias: ' '
        
        Args:
            texto: Texto a corregir
            
        Returns:
            Texto con comillas corregidas
        """
        # Por ahora, implementación simple: reemplazar comillas rectas por latinas
        # TODO: Implementar detección de anidamiento para jerarquía
        
        # Comillas dobles rectas -> latinas
        texto = re.sub(r'"([^"]+)"', f'{self.COMILLA_LATINA_ABRE}\\1{self.COMILLA_LATINA_CIERRA}', texto)
        
        # Comillas inglesas curvas -> latinas (nivel primario)
        texto = texto.replace('"', self.COMILLA_LATINA_ABRE)
        texto = texto.replace('"', self.COMILLA_LATINA_CIERRA)
        
        return texto
    
    def corregir_puntuacion_comillas(self, texto: str) -> str:
        """
        Coloca la puntuación DESPUÉS de las comillas de cierre (norma RAE).
        
        Regla: El punto, coma, punto y coma y dos puntos van DESPUÉS de las comillas.
        
        Ejemplo: "texto". -> «texto».
        
        Args:
            texto: Texto a corregir
            
        Returns:
            Texto con puntuación corregida
        """
        # Buscar patrón: [.,;:] + comilla de cierre
        # Invertir a: comilla de cierre + [.,;:]
        
        patrones = [
            (r'([.,;:])' + re.escape(self.COMILLA_LATINA_CIERRA), 
             self.COMILLA_LATINA_CIERRA + r'\1'),
            (r'([.,;:])' + re.escape(self.COMILLA_INGLESA_CIERRA), 
             self.COMILLA_INGLESA_CIERRA + r'\1'),
            (r'([.,;:])"', '"\\1'),  # Comillas rectas también
        ]
        
        for patron, reemplazo in patrones:
            texto = re.sub(patron, reemplazo, texto)
        
        return texto
    
    def corregir_rayas_dialogos(self, texto: str) -> str:
        """
        Corrige guiones por rayas en diálogos.
        
        Regla: Los diálogos comienzan con raya (—), no guion (-).
        La raya va pegada al texto que sigue.
        
        Args:
            texto: Texto a corregir
            
        Returns:
            Texto con rayas corregidas
        """
        # Detectar inicio de línea (o tras salto de párrafo) + guion + opcionalmente espacio
        # Reemplazar por raya sin espacio
        texto = re.sub(r'^-\s*', self.RAYA, texto, flags=re.MULTILINE)
        texto = re.sub(r'\n-\s*', '\n' + self.RAYA, texto)
        
        return texto
    
    def corregir_rayas_incisos(self, texto: str) -> str:
        """
        Corrige el espaciado de rayas en incisos/aclaraciones.
        
        Regla:
        - Raya de apertura: espacio ANTES, ninguno DESPUÉS
        - Raya de cierre: ninguno ANTES, espacio DESPUÉS
        
        Ejemplo: "texto —inciso— texto" es correcto
        
        Args:
            texto: Texto a corregir
            
        Returns:
            Texto con rayas de inciso corregidas
        """
        # Reemplazar guiones usados como rayas en incisos
        # Patrón: espacio + guion + texto + guion + espacio
        # TODO: Implementación más robusta con detección de contexto
        
        # Por ahora, convertir pares de guiones con espacio a rayas
        texto = re.sub(r'\s+-\s+', f' {self.RAYA}', texto)
        
        return texto
    
    def corregir_espacios_duros(self, texto: str) -> str:
        """
        Inserta espacios duros donde corresponde.
        
        Regla RAE: Espacio duro (non-breaking) antes de:
        - Símbolos de unidades: %, €, $, km, kg, etc.
        - Cifras que no deben separarse
        
        Args:
            texto: Texto a corregir
            
        Returns:
            Texto con espacios duros insertados
        """
        # Espacio antes de símbolo de porcentaje
        texto = re.sub(r'(\d)\s+%', f'\\1{self.ESPACIO_DURO}%', texto)
        
        # Espacio antes de símbolos monetarios que van después
        texto = re.sub(r'(\d)\s+(€|EUR|USD|\$)', f'\\1{self.ESPACIO_DURO}\\2', texto)
        
        # Espacio antes de unidades (km, kg, m, etc.)
        texto = re.sub(r'(\d)\s+(km|kg|m|cm|mm|g|mg|l|ml)', 
                      f'\\1{self.ESPACIO_DURO}\\2', texto, flags=re.IGNORECASE)
        
        return texto

    def corregir_espacios_multiples(self, texto: str) -> str:
        """
        Corrige espacios múltiples (dos o más) por un espacio simple.
        
        Args:
            texto: Texto a corregir
            
        Returns:
            Texto con espacios corregidos
        """
        return re.sub(r'[ ]{2,}', ' ', texto)
    
    def aplicar_todas(self, texto: str) -> str:
        """
        Aplica todas las reglas de ortotipografía en orden.
        
        Args:
            texto: Texto original
            
        Returns:
            Texto con todas las correcciones aplicadas
        """
        # Orden de aplicación importante para evitar conflictos
        texto = self.corregir_comillas(texto)
        texto = self.corregir_puntuacion_comillas(texto)
        texto = self.corregir_rayas_dialogos(texto)
        texto = self.corregir_rayas_incisos(texto)
        texto = self.corregir_espacios_duros(texto)
        texto = self.corregir_espacios_multiples(texto)
        
        return texto


def test_reglas():
    """Función de testing rápido."""
    reglas = OrtotipografiaRules()
    
    # Test comillas
    assert reglas.corregir_comillas('"Hola mundo"') == '«Hola mundo»'
    
    # Test puntuación
    assert reglas.corregir_puntuacion_comillas('«texto»,') == '«texto»,'
    
    # Test espacios duros
    assert '25\xa0%' in reglas.corregir_espacios_duros('25 %')
    
    print("✓ Tests básicos pasados")


if __name__ == '__main__':
    test_reglas()
