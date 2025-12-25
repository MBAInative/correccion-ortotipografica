"""
Detector de problemas de estilo COMPLETO según RAE.
Versión 2: Incluye queísmo/dequeísmo, leísmo/laísmo/loísmo y más.
"""
import spacy
from typing import List, Tuple, Dict
import re


class StyleCheckerV2:
    """Analizador de estilo completo con SpaCy."""
    
    # ═══════════════════════════════════════════════════════════════
    # REDUNDANCIAS (pleonasmos)
    # ═══════════════════════════════════════════════════════════════
    REDUNDANCIAS = {
        'subir arriba': 'subir',
        'bajar abajo': 'bajar',
        'entrar adentro': 'entrar',
        'salir afuera': 'salir',
        'volver a repetir': 'repetir',
        'totalmente gratis': 'gratis',
        'completamente lleno': 'lleno',
        'absolutamente necesario': 'necesario',
        'muy óptimo': 'óptimo',
        'bastante único': 'único',
        'accidente fortuito': 'accidente',
        'cita previa': 'cita',
        'persona humana': 'persona',
        'volar por el aire': 'volar',
        'divisar a lo lejos': 'divisar',
        'mendigo pobre': 'mendigo',
        'protagonista principal': 'protagonista',
        'túnel subterráneo': 'túnel',
        'etc., etcétera': 'etc.',
        'lapso de tiempo': 'lapso',
        'hemorragia de sangre': 'hemorragia',
        'conclusión final': 'conclusión',
        'prever de antemano': 'prever',
        'aterido de frío': 'aterido',
        'erario público': 'erario',
        'falso pretexto': 'pretexto',
        'nexo de unión': 'nexo',
        'regalo gratis': 'regalo',
        'utopía inalcanzable': 'utopía',
        'vigente en la actualidad': 'vigente',
    }
    
    # ═══════════════════════════════════════════════════════════════
    # QUEÍSMO (falta "de" antes de "que")
    # ═══════════════════════════════════════════════════════════════
    VERBOS_QUEISMO = [
        'acordarse', 'alegrarse', 'arrepentirse', 'asegurarse', 'avergonzarse',
        'cerciorarse', 'convencerse', 'cuidarse', 'darse cuenta', 'enterarse',
        'jactarse', 'olvidarse', 'preocuparse', 'quejarse', 'tratarse',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # DEQUEÍSMO (sobra "de" antes de "que")
    # ═══════════════════════════════════════════════════════════════
    VERBOS_DEQUEISMO = [
        'creer', 'pensar', 'opinar', 'considerar', 'suponer', 'imaginar',
        'decir', 'afirmar', 'comunicar', 'expresar', 'manifestar',
        'desear', 'esperar', 'querer', 'pretender', 'intentar',
        'ver', 'oír', 'saber', 'conocer', 'entender', 'comprender',
    ]
    
    # ═══════════════════════════════════════════════════════════════
    # COSISMO
    # ═══════════════════════════════════════════════════════════════
    PATRONES_COSISMO = [
        (r'\bla cosa es que\b', 'el asunto es que', 'Expresión vaga'),
        (r'\balguna cosa\b', 'algo', 'Más específico'),
        (r'\bcualquier cosa\b', 'cualquier elemento/opción', 'Más preciso'),
        (r'\buna cosa\b', '[especificar qué]', 'Término vago'),
        (r'\blas cosas\b', '[especificar qué]', 'Término vago'),
        (r'\bcosas\b', '[especificar]', 'Término genérico'),
    ]
    
    def __init__(self):
        """Inicializa el modelo de SpaCy."""
        try:
            print("⏳ Cargando modelo SpaCy español...")
            self.nlp = spacy.load("es_core_news_sm")
            self.habilitado = True
            print("✓ SpaCy cargado correctamente")
        except Exception as e:
            print(f"⚠️ SpaCy no disponible: {e}")
            self.nlp = None
            self.habilitado = False
    
    # ═══════════════════════════════════════════════════════════════
    # VOZ PASIVA
    # ═══════════════════════════════════════════════════════════════
    def detectar_voz_pasiva(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta construcciones de voz pasiva perifrástica."""
        if not self.habilitado:
            return []
        
        resultados = []
        doc = self.nlp(texto)
        
        for i, token in enumerate(doc):
            if token.lemma_ in ['ser', 'estar'] and i + 1 < len(doc):
                siguiente = doc[i + 1]
                
                # Verificar si siguiente es participio
                verb_form = siguiente.morph.get('VerbForm', [])
                if siguiente.tag_ == 'VLadj' or 'Part' in verb_form:
                    inicio = max(0, i - 2)
                    fin = min(len(doc), i + 4)
                    fragmento = doc[inicio:fin].text
                    
                    resultados.append((
                        fragmento,
                        "Considere voz activa",
                        f"Voz pasiva: '{token.text} {siguiente.text}'"
                    ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # COSISMO
    # ═══════════════════════════════════════════════════════════════
    def detectar_cosismo(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta uso excesivo de 'cosa'."""
        resultados = []
        
        for patron, sugerencia, explicacion in self.PATRONES_COSISMO:
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((match.group(0), sugerencia, explicacion))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # REDUNDANCIAS
    # ═══════════════════════════════════════════════════════════════
    def detectar_redundancias(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta redundancias y pleonasmos."""
        resultados = []
        
        for redundancia, correccion in self.REDUNDANCIAS.items():
            patron = r'\b' + re.escape(redundancia) + r'\b'
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    correccion,
                    "Redundancia: eliminar palabra innecesaria"
                ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # GERUNDIOS INCORRECTOS
    # ═══════════════════════════════════════════════════════════════
    def detectar_gerundios_incorrectos(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta usos incorrectos del gerundio."""
        if not self.habilitado:
            return []
        
        resultados = []
        doc = self.nlp(texto)
        
        for token in doc:
            # Detectar gerundios
            es_gerundio = (
                token.tag_ == 'VMG' or 
                'Ger' in token.morph.get('VerbForm', []) or
                (token.pos_ == 'VERB' and (
                    token.text.endswith('ando') or 
                    token.text.endswith('endo') or
                    token.text.endswith('iendo')
                ))
            )
            
            if es_gerundio:
                inicio = max(0, token.i - 4)
                fin = min(len(doc), token.i + 5)
                fragmento = doc[inicio:fin].text
                
                # Caso 1: Gerundio después de coma
                if token.i > 0 and doc[token.i - 1].text == ',':
                    resultados.append((
                        fragmento,
                        "Reformular con verbo conjugado",
                        "Gerundio de posterioridad (incorrecto)"
                    ))
                
                # Caso 2: Gerundio después de "y"
                elif token.i > 0 and doc[token.i - 1].text.lower() == 'y':
                    resultados.append((
                        fragmento,
                        "Evitar 'y' + gerundio",
                        "Gerundio tras 'y' = posterioridad"
                    ))
                
                # Caso 3: Gerundio al final de oración
                elif token.i < len(doc) - 1 and doc[token.i + 1].text in '.!?':
                    resultados.append((
                        fragmento,
                        "Usar verbo conjugado o subordinada",
                        "Gerundio expresando resultado"
                    ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # QUEÍSMO
    # ═══════════════════════════════════════════════════════════════
    def detectar_queismo(self, texto: str) -> List[Tuple[str, str, str]]:
        """
        Detecta queísmo (falta 'de' antes de 'que').
        
        IMPORTANTE: Algunos verbos son AMBIGUOS:
        - "Se acordó que" puede ser ACORDAR (acuerdo) → correcto SIN "de"
        - "Me acordé que" es ACORDARSE (recordar) → necesita "de"
        
        Solo detectamos casos INEQUÍVOCOS de queísmo.
        """
        resultados = []
        texto_lower = texto.lower()
        
        # Patrones SEGUROS de queísmo (sin ambigüedad)
        patrones = [
            # Verbos pronominales que SIEMPRE requieren "de"
            (r'\bme alegro que\b', 'me alegro de que'),
            (r'\bte alegras que\b', 'te alegras de que'),
            (r'\bse alegra que\b', 'se alegra de que'),
            (r'\bnos alegramos que\b', 'nos alegramos de que'),
            
            # "Acordarse" con pronombre reflexivo = recordar → requiere "de"
            (r'\bme acuerdo que\b', 'me acuerdo de que'),      # Yo recuerdo
            (r'\bte acuerdas que\b', 'te acuerdas de que'),    # Tú recuerdas
            # NOTA: "se acordó que" es AMBIGUO (puede ser acordar/pactar) → NO incluido
            
            # Darse cuenta SIEMPRE requiere "de"
            (r'\bme di cuenta que\b', 'me di cuenta de que'),
            (r'\bse dio cuenta que\b', 'se dio cuenta de que'),
            (r'\bme doy cuenta que\b', 'me doy cuenta de que'),
            
            # Olvidarse SIEMPRE requiere "de"  
            (r'\bme olvidé que\b', 'me olvidé de que'),
            (r'\bse olvidó que\b', 'se olvidó de que'),
            (r'\bme olvido que\b', 'me olvido de que'),
            
            # Enterarse SIEMPRE requiere "de"
            (r'\bme enteré que\b', 'me enteré de que'),
            (r'\bse enteró que\b', 'se enteró de que'),
            
            # Asegurarse SIEMPRE requiere "de"
            (r'\bme aseguré que\b', 'me aseguré de que'),
            (r'\bse aseguró que\b', 'se aseguró de que'),
            
            # Locuciones que SIEMPRE requieren "de"
            (r'\bestoy seguro que\b', 'estoy seguro de que'),
            (r'\bestá seguro que\b', 'está seguro de que'),
            (r'\bno hay duda que\b', 'no hay duda de que'),
            (r'\bno cabe duda que\b', 'no cabe duda de que'),
            (r'\ba pesar que\b', 'a pesar de que'),
            (r'\ben caso que\b', 'en caso de que'),
            (r'\bcon tal que\b', 'con tal de que'),
            (r'\ba fin que\b', 'a fin de que'),
            (r'\ba condición que\b', 'a condición de que'),
        ]
        
        for patron, correccion in patrones:
            for match in re.finditer(patron, texto_lower):
                inicio = match.start()
                fragmento_original = texto[inicio:inicio + len(match.group(0))]
                resultados.append((
                    fragmento_original,
                    correccion,
                    "Queísmo: falta 'de' antes de 'que'"
                ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # DEQUEÍSMO
    # ═══════════════════════════════════════════════════════════════
    def detectar_dequeismo(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta dequeísmo (sobra 'de' antes de 'que')."""
        resultados = []
        
        # Patrones de dequeísmo
        patrones = [
            (r'\bpienso de que\b', 'pienso que'),
            (r'\bcreo de que\b', 'creo que'),
            (r'\bopino de que\b', 'opino que'),
            (r'\bsupongo de que\b', 'supongo que'),
            (r'\bimagino de que\b', 'imagino que'),
            (r'\bdigo de que\b', 'digo que'),
            (r'\bdice de que\b', 'dice que'),
            (r'\bafirmo de que\b', 'afirmo que'),
            (r'\bafirma de que\b', 'afirma que'),
            (r'\bdeseo de que\b', 'deseo que'),
            (r'\bespero de que\b', 'espero que'),
            (r'\bquiero de que\b', 'quiero que'),
            (r'\bsé de que\b', 'sé que'),
            (r'\bveo de que\b', 'veo que'),
            (r'\bme parece de que\b', 'me parece que'),
            (r'\bes seguro de que\b', 'es seguro que'),
            (r'\bes cierto de que\b', 'es cierto que'),
            (r'\bes verdad de que\b', 'es verdad que'),
            (r'\bes posible de que\b', 'es posible que'),
            (r'\bes probable de que\b', 'es probable que'),
        ]
        
        for patron, correccion in patrones:
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    correccion,
                    "Dequeísmo: sobra 'de' antes de 'que'"
                ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # LAÍSMO (uso incorrecto de "la" como objeto indirecto)
    # ═══════════════════════════════════════════════════════════════
    def detectar_laismo(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta laísmo (uso de 'la' en lugar de 'le')."""
        resultados = []
        
        # Patrones comunes de laísmo
        patrones = [
            (r'\bla dije\b', 'le dije'),
            (r'\bla dijeron\b', 'le dijeron'),
            (r'\bla di\b', 'le di'),
            (r'\bla dieron\b', 'le dieron'),
            (r'\bla pregunté\b', 'le pregunté'),
            (r'\bla preguntaron\b', 'le preguntaron'),
            (r'\bla conté\b', 'le conté'),
            (r'\bla contaron\b', 'le contaron'),
            (r'\bla expliqué\b', 'le expliqué'),
            (r'\bla explicaron\b', 'le explicaron'),
            (r'\bla hablé\b', 'le hablé'),
            (r'\bla hablaron\b', 'le hablaron'),
            (r'\bla pedí\b', 'le pedí'),
            (r'\bla pidieron\b', 'le pidieron'),
            (r'\bla contesté\b', 'le contesté'),
            (r'\bla respondí\b', 'le respondí'),
        ]
        
        for patron, correccion in patrones:
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    correccion,
                    "Laísmo: usar 'le' para objeto indirecto femenino"
                ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # LOÍSMO (uso incorrecto de "lo" como objeto indirecto)
    # ═══════════════════════════════════════════════════════════════
    def detectar_loismo(self, texto: str) -> List[Tuple[str, str, str]]:
        """Detecta loísmo (uso de 'lo' en lugar de 'le')."""
        resultados = []
        
        patrones = [
            (r'\blo dije\b', 'le dije'),
            (r'\blo dijeron\b', 'le dijeron'),
            (r'\blo di\b', 'le di'),
            (r'\blo dieron\b', 'le dieron'),
            (r'\blo pregunté\b', 'le pregunté'),
            (r'\blo hablé\b', 'le hablé'),
            (r'\blo conté\b', 'le conté'),
            (r'\blo pedí\b', 'le pedí'),
        ]
        
        for patron, correccion in patrones:
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    correccion,
                    "Loísmo: usar 'le' para objeto indirecto masculino"
                ))
        
        return resultados
    
    # ═══════════════════════════════════════════════════════════════
    # MÉTODO PRINCIPAL
    # ═══════════════════════════════════════════════════════════════
    def analizar_estilo(self, texto: str) -> Dict[str, List[Tuple[str, str, str]]]:
        """Realiza análisis completo de estilo."""
        return {
            'voz_pasiva': self.detectar_voz_pasiva(texto),
            'gerundios': self.detectar_gerundios_incorrectos(texto),
            'queismo': self.detectar_queismo(texto),
            'dequeismo': self.detectar_dequeismo(texto),
            'laismo': self.detectar_laismo(texto),
            'loismo': self.detectar_loismo(texto),
            'cosismo': self.detectar_cosismo(texto),
            'redundancias': self.detectar_redundancias(texto),
        }


if __name__ == '__main__':
    checker = StyleCheckerV2()
    
    texto_test = """
    El documento fue revisado por el equipo. La cosa es que tenemos que 
    subir arriba las escaleras. Me alegro que hayas venido. 
    Creo de que es correcto. La dije la verdad ayer.
    El actor hizo una película, causando gran expectación.
    """
    
    resultados = checker.analizar_estilo(texto_test)
    
    print("\n📊 Resultados de análisis de estilo:\n")
    for categoria, detecciones in resultados.items():
        if detecciones:
            print(f"\n{categoria.upper()}: {len(detecciones)} detecciones")
            for fragmento, sugerencia, explicacion in detecciones[:3]:
                print(f"  - '{fragmento}' → '{sugerencia}'")
                print(f"    ({explicacion})")
