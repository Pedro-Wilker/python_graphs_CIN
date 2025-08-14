import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_date_columns

def render_ag_info_prefeitura():
    st.subheader("Aguardando Informações da Prefeitura")
    
    try:
        df = load_excel('Ag_info_prefeitura')
        
        expected_columns = [
            'CIDADE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Ag_info_prefeitura': {', '.join(missing_columns)}")

        date_cols = ['DATA DA VISITA TÉCNICA']
        df = parse_date_columns(df, date_cols)

        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_info_prefeitura: {str(e)}")
        st.write("Verifique se a aba 'Ag_info_prefeitura' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()