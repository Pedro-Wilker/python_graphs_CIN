import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_chefes_posto():
    st.subheader("Chefes de Posto")
    
    try:
        # Carrega a aba 'Chefes_Posto'
        df = load_excel('Chefes_Posto')
        
        # Colunas esperadas com base em SHEET_CONFIG
        expected_columns = [
            'Cidade', 'Posto', 'Nome', 'E-mail', 'Telefone', 'Turma',
            'Data treinamento', 'Usuário'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Chefes_Posto': {', '.join(missing_columns)}")

        # Processa os dados usando process_sheet_data
        df = process_sheet_data(df, 'Chefes_Posto')

        # Exibe o DataFrame
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Chefes_Posto: {str(e)}")
        st.write("Verifique se a aba 'Chefes_Posto' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()