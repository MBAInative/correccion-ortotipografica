@app.route('/review/<session_id>/<int:page>')
def review_page(session_id, page):
    """Muestra página de revisión con paginación."""
    try:
        # Cargar sesión
        session_file = os.path.join(app.config['SESSIONS_FOLDER'], session_id + '.pkl')
        with open(session_file, 'rb') as f:
            session_data = pickle.load(f)
        
        todas_correcciones = session_data['todas_correcciones']
        
        # Paginación
        per_page = 100
        start = page * per_page
        end = start + per_page
        total_pages = (len(todas_correcciones) + per_page - 1) // per_page
        
        # C orrecciones de esta página
        correcciones_pagina = todas_correcciones[start:end]
        
        # Agrupar por categoría
        from corrector_integrado import CorrectorIntegrado
        corrector_temp = CorrectorIntegrado()
        
        datos_para_template = {}
        for categoria in corrector_temp.CATEGORIAS.keys():
            corrs_categoria = [c for c in correcciones_pagina if c.categoria == categoria]
            if corrs_categoria:
                datos_para_template[categoria] = {
                    'nombre': corrector_temp.CATEGORIAS[categoria],
                    'correcciones': corrs_categoria
                }
        
        return render_template('review_paginated.html',
                             filename=session_data['filename'],
                             session_id=session_id,
                             page=page,
                             total_pages=total_pages,
                             total_correcciones=len(todas_correcciones),
                             correcciones_por_categoria=datos_para_template)
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error al cargar revisión: {str(e)}", 500


