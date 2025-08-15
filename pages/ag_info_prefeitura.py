import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

@st.cache_data
def load_and_process_ag_info_prefeitura():
    """Carrega e processa a aba Ag_info_prefeitura com caching."""
    try:
        raw_df = load_excel('Ag_info_prefeitura')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Ag_info_prefeitura')
        
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].str.replace('\n', ' ', regex=False).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_info_prefeitura: {str(e)}")
        st.stop()

def render_ag_info_prefeitura():
    st.subheader("Aguardando Informações da Prefeitura", icon=":material/info:")
    
    df = load_and_process_ag_info_prefeitura()
    
    expected_columns = [
        'CIDADE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA',
        'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Ag_info_prefeitura': {', '.join(missing_columns)}")
    
    if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
        st.write("Valores únicos em 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA':", df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].unique().tolist())
    if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
        st.write("Valores únicos em 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA':", df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].unique().tolist())
    
    st.write("Amostra dos dados (primeiras 5 linhas):")
    st.dataframe(df.head(5), use_container_width=True)
    
    st.subheader("Tabela Completa")
    st.dataframe(df, use_container_width=True)