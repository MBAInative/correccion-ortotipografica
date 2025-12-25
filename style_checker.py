"""
Detector de problemas de estilo usando SpaCy.
Incluye: voz pasiva, cosismo, redundancias, etc.
"""
import spacy
from typing import List, Tuple, Dict
import re


class StyleChecker:
    """Analizador de estilo con SpaCy."""
    
    # Listas de redundancias comunes
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
    }
    
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
    
    def detectar_voz_pasiva(self, texto: str) -> List[Tuple[str, str, str]]:
        """
        Detecta construcciones de voz pasiva perifrástica.
        
        Returns:
            Lista de (fragmento, sugerencia, explicación)
        """
        if not self.habilitado:
            return []
        
        resultados = []
        doc = self.nlp(texto)
        
        # Buscar patrón: ser/estar + participio
        for i, token in enumerate(doc):
            if token.lemma_ in ['ser', 'estar'] and i + 1 < len(doc):
                siguiente = doc[i + 1]
                
                # Verificar si siguiente es participio
                if siguiente.tag_ == 'VLadj' or 'Part' in siguiente.morph.get('VerbForm'):
                    # Extraer fragmento
                    inicio = max(0, i - 2)
                    fin = min(len(doc), i + 4)
                    fragmento = doc[inicio:fin].text
                    
                    resultados.append((
                        fragmento,
                        f"Considere voz activa",
                        f"Voz pasiva detectada: '{token.text} {siguiente.text}'"
                    ))
        
        return resultados
    
    def detectar_cosismo(self, texto: str) -> List[Tuple[str, str, str]]:
        """
        Detecta uso excesivo de la palabra 'cosa'.
        
        Returns:
            Lista de (fragmento, sugerencia, explicación)
        """
        resultados = []
        
        # Buscar "cosa/s" como sustantivo principal
        patrones = [
            (r'\bla cosa es que\b', 'el asunto es que', 'Expresión vaga'),
            (r'\balguna cosa\b', 'algo', 'Más específico'),
            (r'\bcualquier cosa\b', 'cualquier opción/elemento', 'Más preciso'),
            (r'\buna cosa\b', '[especificar]', 'Término vago'),
            (r'\blas cosas\b', '[especificar]', 'Término vago'),
        ]
        
        for patron, sugerencia, explicacion in patrones:
            for match in re.finditer(patron, texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    sugerencia,
                    explicacion
                ))
        
        return resultados
    
    def detectar_redundancias(self, texto: str) -> List[Tuple[str, str, str]]:
        """
        Detecta redundancias y pleonasmos comunes.
        
        Returns:
            Lista de (fragmento, sugerencia, explicación)
        """
        resultados = []
        
        for redundancia, correccion in self.REDUNDANCIAS.items():
            # Buscar la redundancia (case insensitive)
            for match in re.finditer(r'\b' + re.escape(redundancia) + r'\b', texto, re.IGNORECASE):
                resultados.append((
                    match.group(0),
                    correccion,
                    "Redundancia: eliminar palabra innecesaria"
                ))
        
        return resultados
    
    def detectar_gerundios_incorrectos(self, texto: str) -> List[Tuple[str, str, str]]:
        """
        Detecta posibles usos incorrectos del gerundio.
        Incluye: gerundio de posterioridad, gerundio con "y", gerundio de resultado.
        
        Returns:
            Lista de (fragmento, sugerencia, explicación)
        """
        if not self.habilitado:
            return []
        
        resultados = []
        doc = self.nlp(texto)
        
        for token in doc:
            # Detectar gerundios (pueden tener varios tags dependiendo del modelo)
            es_gerundio = (token.tag_ == 'VMG' or 
                          'Ger' in token.morph.get('VerbForm', []) or
                          token.text.endswith('ando') or 
                          token.text.endswith('endo') or
                          token.text.endswith('iendo'))
            
            if es_gerundio and token.pos_ == 'VERB':
                inicio = max(0, token.i - 4)
                fin = min(len(doc), token.i + 5)
                fragmento = doc[inicio:fin].text
                
                # Caso 1: Gerundio después de coma (posible posterioridad)
                if token.i > 0 and doc[token.i - 1].text == ',':
                    resultados.append((
                        fragmento,
                        "Considere reformular con verbo conjugado",
                        "Posible gerundio de posterioridad (incorrecto)"
                    ))
                
                # Caso 2: Gerundio después de "y" → indica posterioridad
                elif token.i > 0 and doc[token.i - 1].text.lower() == 'y':
                    resultados.append((
                        fragmento,
                        "Reformular: evitar 'y' + gerundio",
                        "Gerundio tras 'y' indica posterioridad (incorrecto)"
                    ))
                
                # Caso 3: Gerundio al final de oración (resultado)
                elif token.i < len(doc) - 1 and doc[token.i + 1].text in '.!?':
                    resultados.append((
                        fragmento,
                        "Considere verbo conjugado o subordinada",
                        "Gerundio expresando resultado o consecuencia"
                    ))
        
        return resultados
    
    def analizar_estilo(self, texto: str) -> Dict[str, List[Tuple[str, str, str]]]:
        """
        Realiza análisis completo de estilo.
        SOLO detecciones con corrección CONCRETA.
        
        Returns:
            Dict con categorías y sus detecciones
        """
        resultados = {
            # HABILITADAS: Detecciones RAE de estilo
            'voz_pasiva': self.detectar_voz_pasiva(texto),
            'gerundios': self.detectar_gerundios_incorrectos(texto),
            'cosismo': self.detectar_cosismo(texto),
            'redundancias': self.detectar_redundancias(texto),
        }
        
        return resultados


if __name__ == '__main__':
    # Test
    checker = StyleChecker()
    
    texto_test = """
    El documento fue revisado por el equipo. La cosa es que tenemos que 
    subir arriba las escaleras. Está completamente lleno el salón.
    """
    
    resultados = checker.analizar_estilo(texto_test)
    
    print("\n📊 Resultados de análisis de estilo:\n")
    for categoria, detecciones in resultados.items():
        if detecciones:
            print(f"\n{categoria.upper()}: {len(detecciones)} detecciones")
            for fragmento, sugerencia, explicacion in detecciones[:3]:
                print(f"  - '{fragmento}' → '{sugerencia}'")
                print(f"    ({explicacion})")
