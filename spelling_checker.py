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
        Inicializa el detector.
        NOTA: La carga del diccionario se retrasa hasta el primer uso (Lazy Loading)
        para evitar timeouts al arrancar la aplicación web en el servidor.
        """
        self.habilitado = False
        self.custom_words: Set[str] = set()
        self.spell = None
        self._diccionario_cargado = False
        self.dict_path_backup = dict_path
        
        print("⏳ SpellingChecker inicializado (carga diferida)")

    def _cargar_diccionario_si_necesario(self):
        """Carga los diccionarios solo si no están cargados aún."""
        if self._diccionario_cargado:
            return

        print("⏳ Iniciando carga de diccionarios (Lazy Load)...")
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        try:
            # 1. Cargar "es_frecuencias.txt" (Corpus masivo)
            # Usamos ruta absoluta para evitar errores en Hostinger/Passenger
            frec_path = os.path.join(base_dir, 'es_frecuencias.txt')
            
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
                                if word.replace('.', '').replace('-', '').isalpha():
                                    self.custom_words.add(word)
                                    count += 1
                        print(f"   ✓ Corpus cargado: {count} formas")
                except Exception as e:
                    print(f"⚠️ Error leyendo corpus: {e}")
            else:
                print(f"⚠️ No se encontró corpus en: {frec_path}")

            # 2. Cargar diccionario local de respaldo (es_full.txt)
            backup_path = os.path.join(base_dir, self.dict_path_backup)
            if os.path.exists(backup_path):
                print(f"   Cargando respaldo: {backup_path}")
                try:
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.strip():
                                self.custom_words.add(line.strip().lower())
                except Exception as e:
                    print(f"⚠️ Error leyendo respaldo: {e}")
            
            # 1.5. Añadir palabras comunes (Stopwords)
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
                'neomarxismo', 'neoliberalismo', 'globalismo', 'identitario', 'identitarios'
            }
            self.custom_words.update(palabras_comunes)

            # 3. Inicializar pyspellchecker
            self.spell = SpellChecker(language='es')
            self.custom_words.update(self.spell.word_frequency.dictionary.keys())
            
            self.habilitado = True
            self._diccionario_cargado = True
            print(f"✓ Diccionario TOTAL cargado: {len(self.custom_words)} formas")
            
        except Exception as e:
            print(f"⚠️ Error crítico cargando diccionario: {e}")
            self.spell = None
            self.habilitado = False
            # Marcar como intentado para no reintentar infinitamente si falla
            self._diccionario_cargado = True

    def _es_palabra_valida(self, palabra: str) -> bool:
        """
        Verifica si una palabra es válida usando diccionario masivo.
        """
        # Asegurar carga
        self._cargar_diccionario_si_necesario()
        
        p = palabra.lower()
        
        # 1. Búsqueda directa (O(1))
        if p in self.custom_words:
            return True

        # Enclíticos simples
        for sufijo in ['lo', 'la', 'los', 'las', 'me', 'te', 'se', 'nos', 'le', 'les']:
            if p.endswith(sufijo):
                raiz = p[:-len(sufijo)]
                if raiz in self.custom_words:
                    if len(raiz) > 3:
                        return True
        return False

    def detectar_errores(self, texto: str, max_errores: int = 50) -> List[Tuple[str, str, str]]:
        """
        Detecta errores ortográficos palabra por palabra.
        """
        if not texto.strip():
            return []
            
        # Asegurar carga del diccionario antes de procesar
        self._cargar_diccionario_si_necesario()
        
        if not self.habilitado:
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