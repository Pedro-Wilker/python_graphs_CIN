import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

@st.cache_data
def load_and_process_ag_visita():
    """Carrega e processa a aba Ag. Visita com caching."""
    try:
        raw_df = load_excel('Ag. Visita')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Ag. Visita')
        
        # Limpeza adicional para colunas específicas
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].str.replace('\n', ' ', regex=False).str.strip()
        if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
            df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].str.replace('\n', ' ', regex=False).str.strip()
        
        st.write("Colunas processadas:", df.columns.tolist())
        st.write("Tipos de dados processados:", df.dtypes.to_dict())
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag. Visita: {str(e)}")
        st.stop()

def render_ag_visita():
    st.subheader("Aguardando Visita Técnica", icon=":material/engineering:")
    
    df = load_and_process_ag_visita()
    
    # Verificar colunas esperadas
    expected_columns = [
        'CIDADE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA',
        'PARECER DA VISITA TÉCNICA', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?',
        'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES', 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Ag. Visita': {', '.join(missing_columns)}")
        # Adicionar colunas ausentes com valores padrão
        for col in missing_columns:
            df[col] = '' if col in ['DATA DA VISITA TÉCNICA', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?', 
                                    'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES', 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] else df[col]
    
    # Exibir valores únicos para colunas críticas
    if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
        st.write("Valores únicos em 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA':", 
                 df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].unique().tolist())
    if 'PARECER DA VISITA TÉCNICA' in df.columns:
        st.write("Valores únicos em 'PARECER DA VISITA TÉCNICA':", 
                 df['PARECER DA VISITA TÉCNICA'].unique().tolist())
    if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
        st.write("Valores únicos em 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA':", 
                 df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].unique().tolist())
    
    # Exibir amostra dos dados
    st.write("Amostra dos dados (primeiras 5 linhas):")
    st.dataframe(df.head(5), use_container_width=True)
    
    # Exibir tabela completa
    st.subheader("Tabela Completa")
    st.dataframe(df, use_container_width=True)