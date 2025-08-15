import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_ag_visita():
    st.subheader("Aguardando Visita Técnica", icon=":material/visibility:")
    
    try:
        raw_df = load_excel('Ag. Visita')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Ag. Visita')
        
        expected_columns = [
            'CIDADE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA',
            'PARECER DA VISITA TÉCNICA', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?',
            'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Ag. Visita': {', '.join(missing_columns)}")
            st.write("Colunas disponíveis:", df.columns.tolist())
        
        if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
            st.write("Valores únicos em 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA':", df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].unique().tolist())
        
        st.write("Amostra dos dados (primeiras 5 linhas):")
        st.dataframe(df.head(5))
        
        st.subheader("Tabela Completa")
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag. Visita: {str(e)}")
        st.write("Verifique se a aba 'Ag. Visita' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()