"""
Reglas de ortotipografía mejoradas según RAE.
Incluye jerarquía de comillas y espaciado correcto con rayas.
"""
import re
from typing import Tuple, List


class OrtotipografiaRulesV2:
    """Reglas ortotipográficas RAE - Versión mejorada."""
    
    # Comillas por nivel (RAE)
    COMILLAS_NIVEL = {
        0: ('«', '»'),  # Latinas - nivel 1
        1: ('"', '"'),  # Inglesas - nivel 2
        2: ("'", "'"),  # Simples - nivel 3
    }
    
    # Otros caracteres
    RAYA = '—'
    ESPACIO_DURO = '\u00A0'
    
    def __init__(self):
        pass
    
    def detectar_nivel_comillas(self, texto: str, pos: int) -> int:
        """
        Determina el nivel de anidamiento de comillas en una posición.
        
        Args:
            texto: Texto completo
            pos: Posición donde detectar nivel
            
        Returns:
            Nivel (0, 1, 2)
        """
        # Contar comillas latinas abiertas antes de pos
        texto_antes = texto[:pos]
        
        latinas_abiertas = texto_antes.count('«')
        latinas_cerradas = texto_antes.count('»')
        nivel_latinas = latinas_abiertas - latinas_cerradas
        
        # Si estamos dentro de latinas, contar inglesas
        if nivel_latinas > 0:
            inglesas_abiertas = texto_antes.count('"')
            inglesas_cerradas = texto_antes.count('"')
            nivel_inglesas = inglesas_abiertas - inglesas_cerradas
            
            if nivel_inglesas > 0:
                return 2  # Nivel 3 (simples)
            else:
                return 1  # Nivel 2 (inglesas)
        
        return 0  # Nivel 1 (latinas)
    
    def corregir_comillas_jerarquia(self, texto: str) -> Tuple[str, int]:
        """
        Convierte comillas respetando jerarquía RAE.
        
        Returns:
            (texto_corregido, num_cambios)
        """
        resultado = texto
        cambios = 0
        
        # Detectar comillas inglesas "texto"
        patron = r'"([^"]+)"'
        
        for match in re.finditer(patron, texto):
            pos_inicio = match.start()
            contenido = match.group(1)
            
            # Determinar nivel
            nivel = self.detectar_nivel_comillas(texto, pos_inicio)
            apertura, cierre = self.COMILLAS_NIVEL[nivel]
            
            # Reemplazar
            original = match.group(0)
            nuevo = f"{apertura}{contenido}{cierre}"
            
            # Solo si hay cambio
            if original != nuevo:
                resultado = resultado.replace(original, nuevo, 1)
                cambios += 1
        
        return resultado, cambios
    
    def corregir_rayas_espaciado(self, texto: str) -> Tuple[str, int]:
        """
        Corrige espaciado con rayas según RAE.
        
        Regla: palabra —inciso— palabra
        - Espacio ANTES de raya inicial
        - SIN espacio después de raya inicial
        - SIN espacio antes de raya final
        - Espacio DESPUÉS de raya final
        
        Returns:
            (texto_corregido, num_cambios)
        """
        resultado = texto
        cambios = 0
        
        # Patrón: Palabra seguida de guion y texto
        # \w—\w\w+—\w  →  debe tener espacios fuera
        
        # Caso 1: palabra—palabra (sin espacios)
        patron1 = r'(\w)(—)(\w)'
        for match in re.finditer(patron1, resultado):
            original = match.group(0)
            reemplazo = f"{match.group(1)} {match.group(2)}{match.group(3)}"
            resultado = resultado.replace(original, reemplazo, 1)
            cambios += 1
        
        # Caso 2: —palabra— sin espacio después de cierre
        patron2 = r'(—\w+—)(\w)'
        for match in re.finditer(patron2, resultado):
            original = match.group(0)
            reemplazo = f"{match.group(1)} {match.group(2)}"
            resultado = resultado.replace(original, reemplazo, 1)
            cambios += 1
        
        # Caso 3: Convertir guiones simples a rayas en diálogos
        # ^-\s  o  \n-\s  →  —
        patron3 = r'(^|\n)-\s+'
        for match in re.finditer(patron3, resultado):
            original = match.group(0)
            reemplazo = f"{match.group(1)}{self.RAYA} "
            resultado = resultado.replace(original, reemplazo, 1)
            cambios += 1
        
        return resultado, cambios
    
    def corregir_espacios_duros(self, texto: str) -> Tuple[str, int]:
        """
        Añade espacios duros antes de %, km, kg, etc.
        
        Returns:
            (texto_corregido, num_cambios)
        """
        resultado = texto
        cambios = 0
        
        # Unidades
        unidades = ['%', 'km', 'kg', 'm', 'cm', 'mm', 'g', 'mg', 'l', 'ml', '€', '$']
        
        for unidad in unidades:
            # \d\s+unidad  →  \d{espacio_duro}unidad
            patron = rf'(\d)\s+{re.escape(unidad)}'
            matches = list(re.finditer(patron, resultado))
            
            for match in matches:
                original = match.group(0)
                reemplazo = f"{match.group(1)}{self.ESPACIO_DURO}{unidad}"
                resultado = resultado.replace(original, reemplazo, 1)
                cambios += 1
        
        return resultado, cambios
    
    def aplicar_todas(self, texto: str) -> str:
        """Aplica todas las reglas."""
        resultado = texto
        
        # 1. Comillas con jerarquía
        resultado, _ = self.corregir_comillas_jerarquia(resultado)
        
        # 2. Rayas con espaciado
        resultado, _ = self.corregir_rayas_espaciado(resultado)
        
        # 3. Espacios duros
        resultado, _ = self.corregir_espacios_duros(resultado)
        
        return resultado


if __name__ == '__main__':
    ortotipo = OrtotipografiaRulesV2()
    
    # Test jerarquía comillas
    texto1 = 'Dijo: "Ella comentó "muy bonito" ayer".'
    corregido1, cambios1 = ortotipo.corregir_comillas_jerarquia(texto1)
    print(f"Original:   {texto1}")
    print(f"Corregido:  {corregido1}")
    print(f"Cambios: {cambios1}\n")
    
    # Test rayas
    texto2 = 'La palabra—dijo—está mal'
    corregido2, cambios2 = ortotipo.corregir_rayas_espaciado(texto2)
    print(f"Original:   {texto2}")
    print(f"Corregido:  {corregido2}")
    print(f"Cambios: {cambios2}\n")
    
    # Test espacios duros
    texto3 = 'Pesa 75 kg y mide 180 cm'
    corregido3, cambios3 = ortotipo.corregir_espacios_duros(texto3)
    print(f"Original:   {texto3}")
    print(f"Corregido:  {corregido3}")
    print(f"Cambios: {cambios3}\n")
