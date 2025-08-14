import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_training_period, parse_date_columns

def render_geral_amplo():
    st.subheader("Geral Amplo")
    
    try:
        df = load_excel('Geral Amplo')
        
        # Colunas esperadas
        expected_columns = [
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA',
            'PARECER DA VISITA TÉCNICA', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?',
            'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES', 'PERÍODO PREVISTO DE TREINAMENTO',
            'TURMA', 'REALIZOU TREINAMENTO?', 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO',
            'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?', 'DATA DA INSTALAÇÃO',
            'DATA DO INÍCIO ATEND.', 'DATA ASSINATURA'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes: {', '.join(missing_columns)}")

        # Tratar período de treinamento
        if 'PERÍODO PREVISTO DE TREINAMENTO' in df.columns:
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)
        
        # Converter colunas de datas
        date_cols = ['DATA DA VISITA TÉCNICA', 'DATA DO D.O.', 'DATA DA INSTALAÇÃO', 
                     'DATA DO INÍCIO ATEND.', 'DATA ASSINATURA']
        df = parse_date_columns(df, date_cols)

        # Exibir tabela
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Geral Amplo: {str(e)}")
        st.stop()