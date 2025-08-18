import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

@st.cache_data
def load_and_process_geral_resumo():
    """Carrega e processa a aba Geral-Resumo com caching."""
    try:
        raw_df = load_excel('Geral-Resumo')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Geral-Resumo')
        
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].str.replace('\n', ' ', regex=False).str.strip()
        if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
            df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].str.replace('\n', ' ', regex=False).str.strip()
        
        st.write("Colunas processadas:", df.columns.tolist())
        st.write("Tipos de dados processados:", df.dtypes.to_dict())
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Geral-Resumo: {str(e)}")
        st.stop()

def render_geral_resumo():
    st.markdown("""
        <h3>Geral Resumo <span class="material-icons" style="vertical-align: middle; color: #004aad;">summarize</span></h3>
    """, unsafe_allow_html=True)
    
    df = load_and_process_geral_resumo()
    
    expected_columns = [
        'CIDADE', 'DATA DE ANÁLISE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA',
        'DATA DA VISITA TÉCNICA', 'PARECER DA VISITA TÉCNICA',
        'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?', 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES',
        'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM',
        'TURMA', 'REALIZOU TREINAMENTO?', 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO',
        'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?', 'DATA DA INSTALAÇÃO',
        'DATA DO INÍCIO ATEND.', 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Geral-Resumo': {', '.join(missing_columns)}")
        for col in missing_columns:
            if col in ['DATA DE ANÁLISE', 'DATA DA VISITA TÉCNICA', 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES',
                       'DATA DO D.O.', 'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.',
                       'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM',
                       'PREVISÃO AJUSTE ESTRUTURA P/ VISITA']:
                df[col] = ''
            elif col == 'TURMA':
                df[col] = 0
            elif col in ['REALIZOU TREINAMENTO?', 'APTO PARA INSTALAÇÃO?']:
                df[col] = False
            else:
                df[col] = ''
    
    if 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA' in df.columns:
        st.write("Valores únicos em 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA':", 
                 df['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].unique().tolist())
    if 'PARECER DA VISITA TÉCNICA' in df.columns:
        st.write("Valores únicos em 'PARECER DA VISITA TÉCNICA':", 
                 df['PARECER DA VISITA TÉCNICA'].unique().tolist())
    if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
        st.write("Valores únicos em 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA':", 
                 df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].unique().tolist())
    
    st.write("Amostra dos dados (primeiras 5 linhas):")
    st.dataframe(df.head(5), use_container_width=True)
    
    st.markdown("### Tabela Completa <span class='material-icons' style='vertical-align: middle; color: #004aad;'>table</span>")
    st.dataframe(df, use_container_width=True)