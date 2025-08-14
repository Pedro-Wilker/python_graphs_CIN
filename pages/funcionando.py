import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_training_period, parse_date_columns

def render_funcionando():
    st.subheader("Funcionando")
    
    try:
        df = load_excel('Funcionando')
        
        expected_columns = [
            'CIDADE', 'DATA DE ANÁLISE', 'PARECER DA VISITA TÉCNICA',
            'PERÍODO PREVISTO DE TREINAMENTO', 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO',
            'DATA DO D.O.', 'APTO PARA INSTALAÇÃO?', 'DATA DA INSTALAÇÃO',
            'DATA DO INÍCIO ATEND.'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Funcionando': {', '.join(missing_columns)}")

        if 'PERÍODO PREVISTO DE TREINAMENTO' in df.columns:
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)
        
        date_cols = ['DATA DE ANÁLISE', 'DATA DO D.O.', 'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.']
        df = parse_date_columns(df, date_cols)

        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Funcionando: {str(e)}")
        st.write("Verifique se a aba 'Funcionando' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()