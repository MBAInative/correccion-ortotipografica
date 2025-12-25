# Script para corregir template
with open(r'templates\review_paginated.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Reemplazar líneas 343-365 con versión corregida
new_section = [
    '                {% for categoria, datos in correcciones_por_categoria.items() %}\n',
    '                {% if datos.correcciones %}\n',
    '                <div class="summary-card">\n',
    '                    <h3>{{ datos.nombre }}</h3>\n',
    '                    <div class="count">{{ datos.correcciones|length }}</div>\n',
    '                    <ul>\n',
    '                        {% if categoria == "ortografia" %}\n',
    '                        <li>Errores tipográficos</li>\n',
    '                        <li>Palabras mal escritas</li>\n',
    '                        {% elif categoria == "ortotipografia" %}\n',
    '                        <li>Jerarquía comillas</li>\n',
    '                        <li>Rayas y guiones</li>\n',
    '                        <li>Espacios duros</li>\n',
    '                        {% elif categoria == "cosismo" %}\n',
    '                        <li>Cosismos detectados</li>\n',
    '                        {% elif categoria == "redundancias" %}\n',
    '                        <li>Expresiones redundantes</li>\n',
    '                        {% endif %}\n',
    '                    </ul>\n',
    '                </div>\n',
    '                {% endif %}\n',
    '                {% endfor %}\n',
]

# Combinar
new_lines = lines[:342] + new_section + lines[365:]

# Guardar
with open(r'templates\review_paginated.html', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✓ Template corregido - líneas 343-365 reemplazadas')
