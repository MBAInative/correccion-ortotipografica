import PyPDF2

# Abrir el archivo PDF
with open('App de corrección ortotipográfica y de estilo.pdf', 'rb') as pdf_file:
    # Crear el lector
    reader = PyPDF2.PdfReader(pdf_file)
    
    # Extraer texto de todas las páginas
    full_text = ""
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        full_text += f"\n--- Página {page_num + 1} ---\n"
        full_text += text
    
    # Guardar en archivo de texto
    with open('requerimientos.txt', 'w', encoding='utf-8') as txt_file:
        txt_file.write(full_text)
    
    print(f"Total de páginas: {len(reader.pages)}")
    print("Texto extraído y guardado en requerimientos.txt")
