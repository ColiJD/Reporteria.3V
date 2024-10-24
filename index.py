import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re
from PIL import Image
# Título de la aplicación
st.title('Procesador de Archivos HTML')

# Cargar la imagen del logo
try:
    logo = Image.open('assets/report.jpg')  # Ajusta la ruta del logo si es necesario
except FileNotFoundError:
    st.sidebar.error('No se encontró la imagen del logo en "assets/logo.webp".')
    logo = None

with st.sidebar:
    if logo:
        st.image(logo, width=150)  # Ajusta el ancho de la imagen si es necesario
    # Subir archivo HTML
    file_path = st.file_uploader("Selecciona un archivo HTML", type=["html", "htm"])
    # Seleccionar el patrón de búsqueda
    tipo = st.selectbox("Tipo de Extracción", ['Patrón con Números'])

# Procesamiento del archivo HTML
if file_path:
    try:
        # Leer el contenido del archivo HTML
        html_content = file_path.read().decode('utf-8')
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Encontrar todos los <nobr> con estilo específico
        nobr_tags = soup.find_all('nobr', {'style': 'background:#fcdec0'})
        
        # Definir los patrones y listas de datos
        pattern = re.compile(r'(\d+)\s+(\d+)\s+(\d{2}\.\d{2}\.\d{4})\s+([A-Za-z0-9\s\-,()/ñÑ]+?)\s+([\d,]+\.\d{2})')
        valid_rows = []
        invalid_rows = []
        
        if nobr_tags:
            for nobr_tag in nobr_tags:
                cleaned_string = nobr_tag.get_text().replace('\xa0', ' ')
                match = pattern.search(cleaned_string)
                
                if match:
                    valid_rows.append([
                        match.group(1),  # ID
                        match.group(2),  # Cantidad
                        match.group(3),  # Fecha
                        match.group(4).strip(),  # Descripción
                        match.group(5)   # Monto
                    ])
                else:
                    invalid_rows.append(cleaned_string)
            
            # Mostrar los resultados
            if tipo == 'Patrón con Números' and valid_rows:
                df_valid = pd.DataFrame(valid_rows, columns=['ID', 'Cantidad', 'Fecha', 'Descripción', 'Monto'])
                st.header("Datos Coincidentes")
                st.dataframe(df_valid)

                df_invalid = pd.DataFrame(invalid_rows, columns=['Texto no coincidente'])
                st.header("Datos No Coincidentes")
                st.dataframe(df_invalid)
                
                # Guardar los resultados en archivos Excel
                # df_valid.to_excel('output_valid.xlsx', index=False)
                # df_invalid.to_excel('output_invalid.xlsx', index=False)
                st.success("Archivos Excel creados con éxito.")
            else:
                st.warning("No se encontraron coincidencias con el patrón especificado.")
        else:
            st.error("No se encontraron <nobr> con el estilo especificado.")
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, sube un archivo HTML para procesar.")
