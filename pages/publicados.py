import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_publicados():
    st.subheader("Publicados")
    
    try:
        # Carrega a aba 'Publicados'
        df = load_excel('Publicados')
        
        # Verifica colunas esperadas
        expected_columns = [
            'CIDADE', 'PARECER DA VISITA TÉCNICA', 'PERÍODO PREVISTO DE TREINAMENTO',
            'REALIZOU TREINAMENTO?', 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO',
            'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?', 'DATA DA INSTALAÇÃO',
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Publicados': {', '.join(missing_columns)}")

        # Processa os dados usando process_sheet_data
        df = process_sheet_data(df, 'Publicados')

        # Exibe o DataFrame
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Publicados: {str(e)}")
        st.write("Verifique se a aba 'Publicados' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()