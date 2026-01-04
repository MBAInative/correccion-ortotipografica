"""
Detector de errores ortográficos mejorado.
Usa diccionario local + heurísticas morfológicas para español.
Optimizado para carga rápida.
"""
from spellchecker import SpellChecker
from typing import List, Tuple, Set
import re
import os

class SpellingChecker:
    """Detector de errores ortográficos robusto con soporte de morfología simple."""
    
    def __init__(self, dict_path='es_full.txt'):
        """
        Inicializa el diccionario combinando pyspellchecker y archivos locales masivos.
        """
        self.habilitado = False
        self.custom_words: Set[str] = set()
        self.spell = None
        
        print("⏳ Inicializando sistema ortográfico avanzado...")
        
        try:
            # 1. Cargar "es_frecuencias.txt" (Massive corpus ~1.2M words)
            # Formato: "palabra frecuencia"
            frec_path = 'es_frecuencias.txt'
            if os.path.exists(frec_path):
                print(f"   Cargando corpus masivo: {frec_path} ...")
                try:
                    with open(frec_path, 'r', encoding='utf-8') as f:
                        # Leer línea a línea optimizado
                        count = 0
                        for line in f:
                            parts = line.split()
                            if parts:
                                word = parts[0].lower()
                                # Filtrar basura (números, símbolos)
                                if word.replace('.', '').replace('-', '').isalpha():
                                    self.custom_words.add(word)
                                    count += 1
                        print(f"   ✓ Corpus cargado: {count} formas")
                except Exception as e:
                    print(f"⚠️ Error leyendo corpus: {e}")

            # 2. Cargar diccionario local simple (backup/normativo)
            if os.path.exists(dict_path):
                print(f"   Cargando diccionario local: {dict_path}")
                try:
                    with open(dict_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                self.custom_words.add(line.strip().lower())
                except Exception as e:
                    print(f"⚠️ Error leyendo diccionario local: {e}")
            
            # 1.5. Añadir palabras comunes (Stopwords) para evitar fallos tontos
            palabras_comunes = {
                'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
                'y', 'e', 'o', 'u', 'pero', 'aunque', 'sin', 'con', 'de', 'del', 'al',
                'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'en',
                'entre', 'hacia', 'hasta', 'para', 'por', 'según', 'sin', 'so', 'sobre', 'tras',
                'yo', 'tú', 'él', 'ella', 'ello', 'nosotros', 'nosotras', 'vosotros', 'vosotras',
                'ellos', 'ellas', 'me', 'te', 'se', 'nos', 'os', 'le', 'les', 'lo', 'la',
                'mi', 'mis', 'tu', 'tus', 'su', 'sus', 'nuestro', 'nuestra', 'nuestros', 'nuestras',
                'que', 'qué', 'cual', 'cuál', 'quien', 'quién', 'cuanto', 'cuánto',
                'como', 'cómo', 'donde', 'dónde', 'cuando', 'cuándo',
                'es', 'son', 'fue', 'fueron', 'era', 'eran', 'ser', 'estar', 'está', 'están',
                'haber', 'ha', 'han', 'había', 'habían', 'hay',
                'tener', 'tengo', 'tiene', 'tienen', 'tenía', 'tenían',
                'hacer', 'hago', 'hace', 'hacen', 'hizo', 'hicieron',
                'ir', 'voy', 'va', 'van', 'fui', 'fueron', 'iba', 'iban',
                'decir', 'dice', 'dicen', 'dijo', 'dijeron',
                'ver', 'veo', 've', 'ven', 'vio', 'vieron',
                'dar', 'doy', 'da', 'dan', 'dio', 'dieron',
                'sí', 'no', 'más', 'muy', 'ya', 'bien', 'mal', 'así', 'todo', 'toda', 'todos', 'todas',
                'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella',
                'aquellos', 'aquellas', 'esto', 'eso', 'aquello',
                'porque', 'pues', 'si', 'tan', 'tanto',
                'neomarxismo', 'neoliberalismo', 'globalismo', 'identitario', 'identitarios' # Añadidos por reporte usuario
            }
            self.custom_words.update(palabras_comunes)

            # 3. Inicializar pyspellchecker (para sugerencias)
            self.spell = SpellChecker(language='es')
            # Añadir palabras del spellchecker al set (lemas base)
            self.custom_words.update(self.spell.word_frequency.dictionary.keys())
            
            self.habilitado = True
            print(f"✓ Sistema listo. Total formas únicas: {len(self.custom_words)}")
            
        except Exception as e:
            print(f"⚠️ Error crítico en diccionario: {e}")
            self.spell = None

    def _es_palabra_valida(self, palabra: str) -> bool:
        """
        Verifica si una palabra es válida usando diccionario masivo.
        Al tener 1.2M de formas, las heurísticas son innecesarias y peligrosas.
        """
        p = palabra.lower()
        
        # 1. Búsqueda directa (O(1)) - Cubre plurales y conjugaciones gracias al corpus
        if p in self.custom_words:
            return True

        # Enclíticos simples (dímelo, comprarlo) - Estos SÍ merecen conservarse
        # porque el corpus podría no tener todas las combinaciones verbo+pronombre
        for sufijo in ['lo', 'la', 'los', 'las', 'me', 'te', 'se', 'nos', 'le', 'les']:
            if p.endswith(sufijo):
                raiz = p[:-len(sufijo)]
                if raiz in self.custom_words:
                    # Validar que la raiz sea verbo (difícil sin POS tagger)
                    # Pero si 'amar' está y tenemos 'amarlo', es seguro.
                    # Riesgo: 'palo' -> 'pa' (no verbo).
                    # Filtro: raiz debe terminar en r, s, n, vocal acentuada...
                    # Simplificación: aceptar si la raíz es larga (>3 chars) y existe.
                    if len(raiz) > 3:
                        return True
                
                # Caso infinitivo+pronombre: amar + lo -> amarlo (raiz=amar) -> OK
                # Caso gerundio+pronombre: amando + lo -> amándolo (raiz=amándo -> amando)
                # Esto requeriría quitar tilde. Complejo.
        
        return False

    def detectar_errores(self, texto: str, max_errores: int = 50) -> List[Tuple[str, str, str]]:
        """
        Detecta errores ortográficos palabra por palabra.
        """
        if not self.habilitado or not texto.strip():
            return []
            
        resultados = []
        
        # Tokenizar texto
        palabras_encontradas = re.finditer(r'\b([a-záéíóúñü]+)\b', texto, re.IGNORECASE)
        
        errores_count = 0
        palabras_verificadas = set()
        
        for match in palabras_encontradas:
            if errores_count >= max_errores:
                break
                
            palabra = match.group(1)
            
            if not palabra[0].islower():
                continue
                
            p_lower = palabra.lower()
            if p_lower in palabras_verificadas:
                continue
                
            if self._es_palabra_valida(p_lower):
                palabras_verificadas.add(p_lower)
                continue
                
            # Error confirmado
            correccion = self.spell.correction(p_lower)
            if not correccion or correccion == p_lower:
                sugerencia = "(sin sugerencia)"
            else:
                sugerencia = correccion
                
            resultados.append((
                palabra,
                sugerencia,
                f"Ortografía: '{palabra}' no encontrada"
            ))
            errores_count += 1
            palabras_verificadas.add(p_lower)
                    
        return resultados

if __name__ == '__main__':
    # Test
    checker = SpellingChecker()
    
    texto_test = "Los años han tenido hijos estudiosos. El coche enpieza a correr. Campesinos y obreros defendiendo."
    print(f"\nTexto: {texto_test}")
    
    errores = checker.detectar_errores(texto_test)
    
    print("\nResultados:")
    for error, corr, expl in errores:
        print(f"  ✗ '{error}' → '{corr}'")