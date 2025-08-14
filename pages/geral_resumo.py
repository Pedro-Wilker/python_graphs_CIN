import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_training_period, parse_date_columns

def render_geral_resumo():
    st.subheader("Geral Resumo")
    
    try:
        # Carregar a aba 'Geral-Resumo'
        df = load_excel('Geral-Resumo')
        
        # Colunas esperadas
        expected_columns = [
            'CIDADE', 'DATA DE ANÁLISE', 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA',
            'DATA DA VISITA TÉCNICA', 'PARECER DA VISITA TÉCNICA',
            'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?', 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES',
            'PERÍODO PREVISTO DE TREINAMENTO', 'TURMA', 'REALIZOU TREINAMENTO?',
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO', 'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?',
            'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'Status', 'Qtd.'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Geral-Resumo': {', '.join(missing_columns)}")

        # Tratar período de treinamento
        if 'PERÍODO PREVISTO DE TREINAMENTO' in df.columns:
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)
        
        # Converter colunas de datas
        date_cols = [
            'DATA DE ANÁLISE', 'DATA DA VISITA TÉCNICA', 'DATA DO D.O.',
            'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.'
        ]
        df = parse_date_columns(df, date_cols)

        # Tratar valores vazios ou com '-'
        for col in ['ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?', 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES']:
            if col in df.columns:
                df[col] = df[col].replace('-', 'Não informado').fillna('Não informado')

        # Exibir tabela
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Geral Resumo: {str(e)}")
        st.write("Verifique se a aba 'Geral-Resumo' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()