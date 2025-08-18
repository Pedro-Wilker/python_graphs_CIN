import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_funcionando():
    st.subheader("Funcionando")
    
    try:
        # Carrega a aba 'Funcionando'
        df = load_excel('Funcionando')
        
        # Verifica colunas esperadas
        expected_columns = [
            'CIDADE', 'DATA DE ANÁLISE', 'PARECER DA VISITA TÉCNICA',
            'PERÍODO PREVISTO DE TREINAMENTO', 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO',
            'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?', 'DATA DA INSTALAÇÃO',
            'DATA DO INÍCIO ATEND.'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Funcionando': {', '.join(missing_columns)}")

        # Processa os dados usando process_sheet_data
        df = process_sheet_data(df, 'Funcionando')

        # Exibe o DataFrame
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Funcionando: {str(e)}")
        st.write("Verifique se a aba 'Funcionando' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()