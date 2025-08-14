import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_visitas_realizadas():
    st.subheader("Visitas Realizadas")
    try:
        df = load_excel('Visitas Realizadas')
        df = process_sheet_data(df, 'Visitas Realizadas')
        st.dataframe(df)
        
        # Subtotal
        st.subheader("Subtotal")
        total_visitas = len(df)
        visitas_aprovadas = len(df[df['PARECER DA VISITA TÉCNICA'] == 'Aprovado'])
        visitas_reprovadas = len(df[df['PARECER DA VISITA TÉCNICA'] == 'Reprovado'])
        subtotal_data = {
            'Total de visitas': [total_visitas],
            'Visitas aprovadas': [visitas_aprovadas],
            'Visitas Reprovadas': [visitas_reprovadas]
        }
        st.dataframe(pd.DataFrame(subtotal_data))
    except Exception as e:
        st.error(f"Erro ao processar a aba Visitas Realizadas: {str(e)}")
        st.stop()