import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_visitas_realizadas():
    st.subheader("Visitas Realizadas", icon=":material/check_circle:")
    
    try:
        raw_df = load_excel('Visitas Realizadas')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Visitas Realizadas')
        
        expected_columns = [
            'CIDADE', 'DATA DE ANÁLISE', 'DATA DA VISITA TÉCNICA',
            'ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS?'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Visitas Realizadas': {', '.join(missing_columns)}")
            st.write("Colunas disponíveis:", df.columns.tolist())
        
        st.subheader("Subtotal")
        total_visits = len(df)
        st.metric("Total de Visitas", total_visits)
        
        st.write("Amostra dos dados (primeiras 5 linhas):")
        st.dataframe(df.head(5))
        
        st.subheader("Tabela Completa")
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"Erro ao processar a aba Visitas Realizadas: {str(e)}")
        st.write("Verifique se a aba 'Visitas Realizadas' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()