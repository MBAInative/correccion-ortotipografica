"""
Reglas de ortotipografía COMPLETAS según RAE.
Versión 3: Incluye TODAS las recomendaciones ortotipográficas.
"""
import re
from typing import Tuple, List, Dict


class OrtotipografiaRulesV3:
    """Reglas ortotipográficas RAE - Versión completa."""
    
    # ═══════════════════════════════════════════════════════════════
    # COMILLAS
    # ═══════════════════════════════════════════════════════════════
    COMILLAS_NIVEL = {
        0: ('«', '»'),  # Latinas - nivel 1
        1: ('"', '"'),  # Inglesas - nivel 2
        2: ("'", "'"),  # Simples - nivel 3
    }
    
    # ═══════════════════════════════════════════════════════════════
    # CARACTERES ESPECIALES
    # ═══════════════════════════════════════════════════════════════
    RAYA = '—'
    ESPACIO_DURO = '\u00A0'
    
    # ═══════════════════════════════════════════════════════════════
    # MAYÚSCULAS (RAE: deben ir en minúscula)
    # ═══════════════════════════════════════════════════════════════
    DIAS_SEMANA = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
    MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 
             'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    ESTACIONES = ['primavera', 'verano', 'otoño', 'invierno']
    
    # ═══════════════════════════════════════════════════════════════
    # ABREVIATURAS RAE (deben llevar punto)
    # ═══════════════════════════════════════════════════════════════
    ABREVIATURAS = {
        'Sr': 'Sr.', 'Sra': 'Sra.', 'Srta': 'Srta.',
        'Dr': 'Dr.', 'Dra': 'Dra.',
        'Ud': 'Ud.', 'Uds': 'Uds.',
        'Vd': 'Vd.', 'Vds': 'Vds.',
        'etc': 'etc.', 'Etc': 'Etc.',
        'pág': 'pág.', 'págs': 'págs.',
        'núm': 'núm.', 'núms': 'núms.',
        'vol': 'vol.', 'vols': 'vols.',
        'cap': 'cap.', 'caps': 'caps.',
        'fig': 'fig.', 'figs': 'figs.',
        'ej': 'ej.', 'p ej': 'p. ej.',
        'vs': 'vs.',
        'aprox': 'aprox.',
        'máx': 'máx.', 'mín': 'mín.',
    }
    
    # ═══════════════════════════════════════════════════════════════
    # SIGLAS (sin puntos internos)
    # ═══════════════════════════════════════════════════════════════
    SIGLAS_INCORRECTAS = {
        'O.N.U.': 'ONU',
        'O.T.A.N.': 'OTAN',
        'U.E.': 'UE',
        'E.E.U.U.': 'EE. UU.',
        'EE.UU.': 'EE. UU.',
        'EEUU': 'EE. UU.',
        'CC.OO.': 'CC. OO.',
        'FF.AA.': 'FF. AA.',
    }
    
    # ═══════════════════════════════════════════════════════════════
    # EXTRANJERISMOS COMUNES (sugerir cursiva o alternativa)
    # ═══════════════════════════════════════════════════════════════
    EXTRANJERISMOS = {
        'software': 'programa informático',
        'hardware': 'equipo informático',
        'email': 'correo electrónico',
        'e-mail': 'correo electrónico',
        'online': 'en línea',
        'on-line': 'en línea',
        'offline': 'sin conexión',
        'feedback': 'retroalimentación',
        'marketing': 'mercadotecnia',
        'manager': 'gerente/director',
        'link': 'enlace',
        'click': 'clic',
        'smartphone': 'teléfono inteligente',
        'laptop': 'portátil',
        'backup': 'copia de seguridad',
        'chat': 'conversación/charla',
        'post': 'publicación',
        'hashtag': 'etiqueta',
        'startup': 'empresa emergente',
        'ranking': 'clasificación',
        'hobby': 'afición/pasatiempo',
        'show': 'espectáculo',
        'parking': 'aparcamiento',
        'stop': 'alto',
        'spray': 'aerosol',
        'stock': 'existencias',
        'estrés': 'estrés',  # Ya adaptado, OK
    }
    
    # ═══════════════════════════════════════════════════════════════
    # UNIDADES (espacio duro antes)
    # ═══════════════════════════════════════════════════════════════
    UNIDADES = ['%', 'km', 'kg', 'm', 'cm', 'mm', 'g', 'mg', 'l', 'ml', 
                '€', '$', 'h', 's', 'min', 'Hz', 'kHz', 'MHz', 'GB', 'MB', 'KB']
    
    def __init__(self):
        pass
    
    # ═══════════════════════════════════════════════════════════════
    # COMILLAS
    # ═══════════════════════════════════════════════════════════════
    def detectar_nivel_comillas(self, texto: str, pos: int) -> int:
        """Determina el nivel de anidamiento de comillas."""
        texto_antes = texto[:pos]
        latinas_abiertas = texto_antes.count('«') - texto_antes.count('»')
        
        if latinas_abiertas > 0:
            inglesas_abiertas = texto_antes.count('"') - texto_antes.count('"')
            return 2 if inglesas_abiertas > 0 else 1
        return 0
    
    def corregir_comillas_jerarquia(self, texto: str) -> Tuple[str, int]:
        """Convierte comillas respetando jerarquía RAE."""
        resultado = texto
        cambios = 0
        
        for match in re.finditer(r'"([^"]+)"', texto):
            nivel = self.detectar_nivel_comillas(texto, match.start())
            apertura, cierre = self.COMILLAS_NIVEL[nivel]
            original = match.group(0)
            nuevo = f"{apertura}{match.group(1)}{cierre}"
            
            if original != nuevo:
                resultado = resultado.replace(original, nuevo, 1)
                cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # RAYAS
    # ═══════════════════════════════════════════════════════════════
    def corregir_rayas_espaciado(self, texto: str) -> Tuple[str, int]:
        """Corrige espaciado con rayas según RAE."""
        resultado = texto
        cambios = 0
        
        # palabra—palabra → palabra —palabra
        for match in re.finditer(r'(\w)(—)(\w)', resultado):
            resultado = resultado.replace(match.group(0), 
                f"{match.group(1)} {match.group(2)}{match.group(3)}", 1)
            cambios += 1
        
        # —palabra—palabra → —palabra— palabra
        for match in re.finditer(r'(—\w+—)(\w)', resultado):
            resultado = resultado.replace(match.group(0), 
                f"{match.group(1)} {match.group(2)}", 1)
            cambios += 1
        
        # Guion a raya en diálogos
        for match in re.finditer(r'(^|\n)-\s+', resultado):
            resultado = resultado.replace(match.group(0), 
                f"{match.group(1)}{self.RAYA} ", 1)
            cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # ESPACIOS DUROS
    # ═══════════════════════════════════════════════════════════════
    def corregir_espacios_duros(self, texto: str) -> Tuple[str, int]:
        """Añade espacios duros antes de unidades."""
        resultado = texto
        cambios = 0
        
        for unidad in self.UNIDADES:
            patron = rf'(\d)\s+{re.escape(unidad)}(?!\w)'
            for match in re.finditer(patron, resultado):
                resultado = resultado.replace(match.group(0), 
                    f"{match.group(1)}{self.ESPACIO_DURO}{unidad}", 1)
                cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # MAYÚSCULAS INCORRECTAS (con detección de nombres propios)
    # ═══════════════════════════════════════════════════════════════
    def es_parte_nombre_propio(self, texto: str, pos: int, palabra: str) -> bool:
        """
        Detecta si una palabra forma parte de un nombre propio.
        Ejemplos: "Domingo de Soto", "Primero de Mayo", "Palacio de Verano"
        """
        # Obtener contexto antes y después
        texto_antes = texto[:pos].strip()
        texto_despues = texto[pos + len(palabra):].strip()
        
        # Si está precedido por palabra con mayúscula (ej: "Domingo de Soto" → Domingo)
        palabras_antes = texto_antes.split()
        if palabras_antes:
            ultima_palabra = palabras_antes[-1]
            # Si la palabra anterior termina con mayúscula o tiene mayúscula
            if ultima_palabra and ultima_palabra[0].isupper():
                return True
            # Si hay "de" antes con nombre propio (Palacio de Verano)
            if len(palabras_antes) >= 2:
                if palabras_antes[-1].lower() == 'de' and palabras_antes[-2][0].isupper():
                    return True
        
        # Si está seguido por "de" + palabra con mayúscula
        palabras_despues = texto_despues.split()
        if len(palabras_despues) >= 2:
            if palabras_despues[0].lower() == 'de' and palabras_despues[1][0].isupper():
                return True
        
        # Si está seguido directamente por palabra con mayúscula
        if palabras_despues and palabras_despues[0][0].isupper():
            return True
        
        # Si viene después de preposición "de" que sigue a mayúscula
        # Ej: "Primero de Mayo" - Mayo viene después de "de" que sigue a "Primero"
        if len(palabras_antes) >= 2:
            if palabras_antes[-1].lower() == 'de':
                # Buscar la palabra antes del "de"
                for i in range(len(palabras_antes) - 2, -1, -1):
                    if palabras_antes[i][0].isupper():
                        return True
                    break
        
        return False
    
    def corregir_mayusculas(self, texto: str) -> Tuple[str, int]:
        """
        Corrige mayúsculas incorrectas en días, meses, estaciones.
        RESPETA nombres propios como 'Domingo de Soto', 'Primero de Mayo'.
        """
        resultado = texto
        cambios = 0
        
        todas_palabras = self.DIAS_SEMANA + self.MESES + self.ESTACIONES
        
        for palabra in todas_palabras:
            palabra_mayus = palabra.capitalize()
            
            # Buscar todas las ocurrencias
            patron = rf'\b{palabra_mayus}\b'
            
            for match in re.finditer(patron, resultado):
                pos = match.start()
                
                # Verificar si está al inicio de oración (no corregir)
                texto_antes = resultado[:pos].rstrip()
                if texto_antes == '' or texto_antes[-1] in '.!?¿¡':
                    continue
                
                # Verificar si forma parte de nombre propio (no corregir)
                if self.es_parte_nombre_propio(resultado, pos, palabra_mayus):
                    continue
                
                # Si llegamos aquí, es un uso incorrecto de mayúscula
                resultado = resultado[:pos] + palabra + resultado[pos + len(palabra_mayus):]
                cambios += 1
        
        return resultado, cambios

    
    # ═══════════════════════════════════════════════════════════════
    # ABREVIATURAS
    # ═══════════════════════════════════════════════════════════════
    def corregir_abreviaturas(self, texto: str) -> Tuple[str, int]:
        """Corrige abreviaturas sin punto."""
        resultado = texto
        cambios = 0
        
        for abrev_sin, abrev_con in self.ABREVIATURAS.items():
            # Solo reemplazar si NO tiene punto después
            patron = rf'\b{re.escape(abrev_sin)}(?!\.)\b'
            for match in re.finditer(patron, resultado):
                resultado = resultado[:match.start()] + abrev_con + resultado[match.end():]
                cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # SIGLAS
    # ═══════════════════════════════════════════════════════════════
    def corregir_siglas(self, texto: str) -> Tuple[str, int]:
        """Corrige siglas con puntos incorrectos."""
        resultado = texto
        cambios = 0
        
        for sigla_mal, sigla_bien in self.SIGLAS_INCORRECTAS.items():
            if sigla_mal in resultado:
                resultado = resultado.replace(sigla_mal, sigla_bien)
                cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # NÚMEROS (formato español)
    # ═══════════════════════════════════════════════════════════════
    def corregir_numeros(self, texto: str) -> Tuple[str, int]:
        """Corrige formato de números según RAE española."""
        resultado = texto
        cambios = 0
        
        # Punto decimal → coma decimal (3.14 → 3,14)
        patron_decimal = r'(\d+)\.(\d{1,2})(?!\d)'
        for match in re.finditer(patron_decimal, resultado):
            original = match.group(0)
            nuevo = f"{match.group(1)},{match.group(2)}"
            resultado = resultado.replace(original, nuevo, 1)
            cambios += 1
        
        # Horas: 13:30h → 13:30 h (espacio antes de h)
        patron_hora = r'(\d{1,2}:\d{2})h\b'
        for match in re.finditer(patron_hora, resultado):
            resultado = resultado.replace(match.group(0), 
                f"{match.group(1)} h", 1)
            cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # PUNTUACIÓN AVANZADA
    # ═══════════════════════════════════════════════════════════════
    def corregir_puntuacion(self, texto: str) -> Tuple[str, int]:
        """Corrige errores de puntuación según RAE."""
        resultado = texto
        cambios = 0
        
        # Coma antes de "pero" (si falta)
        patron_pero = r'(\w)\s+pero\b'
        for match in re.finditer(patron_pero, resultado, re.IGNORECASE):
            if match.group(1) not in ',;:':
                original = match.group(0)
                nuevo = f"{match.group(1)}, pero"
                resultado = resultado.replace(original, nuevo, 1)
                cambios += 1
        
        # Coma antes de "aunque"
        patron_aunque = r'(\w)\s+aunque\b'
        for match in re.finditer(patron_aunque, resultado, re.IGNORECASE):
            if match.group(1) not in ',;:':
                original = match.group(0)
                nuevo = f"{match.group(1)}, aunque"
                resultado = resultado.replace(original, nuevo, 1)
                cambios += 1
        
        # Coma antes de "sino"
        patron_sino = r'(\w)\s+sino\b'
        for match in re.finditer(patron_sino, resultado, re.IGNORECASE):
            if match.group(1) not in ',;:':
                original = match.group(0)
                nuevo = f"{match.group(1)}, sino"
                resultado = resultado.replace(original, nuevo, 1)
                cambios += 1
        
        return resultado, cambios
    
    # ═══════════════════════════════════════════════════════════════
    # EXTRANJERISMOS
    # ═══════════════════════════════════════════════════════════════
    def detectar_extranjerismos(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta extranjerismos y sugiere alternativas."""
        resultados = []
        
        for extranjerismo, alternativa in self.EXTRANJERISMOS.items():
            patron = rf'\b{re.escape(extranjerismo)}\b'
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    alternativa,
                    f"Extranjerismo: usar '{alternativa}' o escribir en cursiva"
                ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # MÉTODO PRINCIPAL
    # ═══════════════════════════════════════════════════════════════
    def aplicar_todas(self, texto: str) -> str:
        """Aplica todas las reglas ortotipográficas."""
        resultado = texto
        
        resultado, _ = self.corregir_comillas_jerarquia(resultado)
        resultado, _ = self.corregir_rayas_espaciado(resultado)
        resultado, _ = self.corregir_espacios_duros(resultado)
        resultado, _ = self.corregir_mayusculas(resultado)
        resultado, _ = self.corregir_abreviaturas(resultado)
        resultado, _ = self.corregir_siglas(resultado)
        resultado, _ = self.corregir_numeros(resultado)
        resultado, _ = self.corregir_puntuacion(resultado)
        
        return resultado
    
    def obtener_explicacion(self, texto_original: str, texto_corregido: str) -> str:
        """Genera explicación de los cambios realizados."""
        if '«' in texto_corregido and '"' in texto_original:
            return 'Jerarquía de comillas RAE (« > " > \')'
        elif '—' in texto_corregido and '—' not in texto_original:
            return 'Rayas con espaciado correcto'
        elif self.ESPACIO_DURO in texto_corregido:
            return 'Espacio duro antes de unidades'
        elif any(m.lower() in texto_corregido.lower() for m in self.MESES):
            return 'Mayúsculas: meses en minúscula'
        elif any(d.lower() in texto_corregido.lower() for d in self.DIAS_SEMANA):
            return 'Mayúsculas: días en minúscula'
        elif ', pero' in texto_corregido or ', aunque' in texto_corregido:
            return 'Puntuación: coma antes de conjunción adversativa'
        else:
            return 'Corrección ortotipográfica RAE'


if __name__ == '__main__':
    ortotipo = OrtotipografiaRulesV3()
    
    # Tests
    tests = [
        ('Dijo: "Ella dijo \"hola\" ayer".', 'Comillas'),
        ('Llegó el Lunes de Enero.', 'Mayúsculas'),
        ('El Dr habló con la Sra', 'Abreviaturas'),
        ('La O.N.U. y EE.UU.', 'Siglas'),
        ('Son 3.14 metros', 'Números'),
        ('Vino pero no se quedó', 'Puntuación'),
        ('Necesito feedback urgente', 'Extranjerismos'),
    ]
    
    for texto, categoria in tests:
        corregido = ortotipo.aplicar_todas(texto)
        extranjerismos = ortotipo.detectar_extranjerismos(texto)
        print(f"\n{categoria}:")
        print(f"  Original:  {texto}")
        print(f"  Corregido: {corregido}")
        if extranjerismos:
            print(f"  Extranjerismos: {extranjerismos}")
