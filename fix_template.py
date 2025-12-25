import re

# Leer archivo
with open(r'C:\Users\lbt00\OneDrive\Documentos\Proyectos\correccion_ortotipografica\templates\review_paginated.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Buscar y reemplazar la sección problemática
old_section = r'''{% set stats_data = \{
                'ortografia': \{'title': 'Ortografía', 'items': \['Errores tipográficos', 'Palabras mal escritas'\]\},
                'ortotipografia': \{'title': 'Ortotipografía RAE', 'items': \['Jerarquía comillas', 'Rayas y guiones',
                'Espacios duros'\]\},
                'cosismo': \{'title': 'Uso de "cosa"', 'items': \['Cosismos detectados'\]\},
                'redundancias': \{'title': 'Redundancias', 'items': \['Expresiones redundantes'\]\}
                \} %}

                {% for cat_key, cat_info in stats_data\.items\(\) %}
                {% if cat_key in correcciones_por_categoria and
                correcciones_por_categoria\[cat_key\]\['correcciones'\]\|length > 0 %}
                {% set count = correcciones_por_categoria\[cat_key\]\['correcciones'\]\|length %}
                <div class="summary-card">
                    <h3>\{\{ cat_info\.title \}\}</h3>
                    <div class="count">\{\{ count \}\}</div>
                    <ul>
                        {% for item in cat_info\.items %}
                        <li>\{\{ item \}\}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
                {% endfor %}'''

new_section = '''{% for categoria, datos in correcciones_por_categoria.items() %}
                {% if datos.correcciones %}
                <div class="summary-card">
                    <h3>{{ datos.nombre }}</h3>
                    <div class="count">{{ datos.correcciones|length }}</div>
                    <ul>
                        {% if categoria == 'ortografia' %}
                        <li>Errores tipográficos</li>
                        <li>Palabras mal escritas</li>
                        {% elif categoria == 'ortotipografia' %}
                        <li>Jerarquía comillas</li>
                        <li>Rayas y guiones</li>
                        <li>Espacios duros</li>
                        {% elif categoria == 'cosismo' %}
                        <li>Cosismos detectados</li>
                        {% elif categoria == 'redundancias' %}
                        <li>Expresiones redundantes</li>
                        {% endif %}
                    </ul>
                </div>
                {% endif %}
                {% endfor %}'''

# Hacer reemplazo
new_content = re.sub(old_section, new_section, content, flags=re.DOTALL)

# Guardar
with open(r'C:\Users\lbt00\OneDrive\Documentos\Proyectos\correccion_ortotipografica\templates\review_paginated.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✓ Archivo actualizado")
