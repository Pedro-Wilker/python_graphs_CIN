import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_date_columns

def render_ag_visita():
    st.subheader("Aguardando Visita Técnica")
    
    try:
        # Load the 'Ag. Visita' sheet
        df = load_excel('Ag. Visita')
        
        # Expected columns
        expected_columns = [
            'CIDADE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA',
            'PARECER DA VISITA TÉCNICA', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?',
            'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Ag. Visita': {', '.join(missing_columns)}")

        # Convert date columns
        date_cols = ['DATA DA VISITA TÉCNICA']
        df = parse_date_columns(df, date_cols)

        # Handle empty or '-' values
        for col in ['ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?', 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES']:
            if col in df.columns:
                df[col] = df[col].replace('-', 'Não informado').fillna('Não informado')

        # Display the table
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Ag. Visita: {str(e)}")
        st.write("Verifique se a aba 'Ag. Visita' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()