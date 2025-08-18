import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data, parse_training_period

def render_instalados():
    st.subheader("Instalados")
    
    try:
        # Carrega a aba 'Instalados'
        df = load_excel('Instalados')
        
        # Verifica colunas esperadas
        expected_columns = [
            'CIDADE', 'PARECER DA VISITA TÉCNICA', 'PERÍODO PREVISTO DE TREINAMENTO',
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO', 'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?',
            'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Instalados': {', '.join(missing_columns)}")

        # Processa os dados usando process_sheet_data
        df = process_sheet_data(df, 'Instalados')

        # Exibe o DataFrame
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Instalados: {str(e)}")
        st.write("Verifique se a aba 'Instalados' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()