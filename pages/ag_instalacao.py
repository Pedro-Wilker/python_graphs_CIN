import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

@st.cache_data
def load_and_process_ag_instalacao():
    """Carrega e processa a aba Ag_Instalacao com caching."""
    try:
        raw_df = load_excel('Ag_Instalacao')
        
        df = process_sheet_data(raw_df, 'Ag_Instalacao')
        
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].str.replace('\n', ' ', regex=False).str.strip()
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_Instalacao: {str(e)}")
        st.stop()

def render_ag_instalacao():
    st.markdown("""
        <h3>Aguardando Instalação <span class="material-icons" style="vertical-align: middle; color: #004aad;">construction</span></h3>
    """, unsafe_allow_html=True)
    
    df = load_and_process_ag_instalacao()
    
    expected_columns = [
        'CIDADE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'PARECER DA VISITA TÉCNICA',
        'REALIZOU TREINAMENTO?', 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO',
        'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?', 'DATA DA INSTALAÇÃO',
        'DATA DO INÍCIO ATEND.', 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO',
        'PERÍODO PREVISTO DE TREINAMENTO_FIM', 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Ag_Instalacao': {', '.join(missing_columns)}")
    
    if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
        st.write("Valores únicos em 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA':", df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].unique().tolist())
    if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
        st.write("Valores únicos em 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA':", df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].unique().tolist())
 
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)