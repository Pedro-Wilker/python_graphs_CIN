import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_training_period

def render_treina_turma():
    st.subheader("Treinamento por Turma")
    
    try:
        df = load_excel('Treina-turma')
        
        expected_columns = [
            'CIDADE', 'PERÍODO PREVISTO DE TREINAMENTO', 'TURMA', 'REALIZOU TREINAMENTO?'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Treina-turma': {', '.join(missing_columns)}")

        if 'PERÍODO PREVISTO DE TREINAMENTO' in df.columns:
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)

        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Treina-turma: {str(e)}")
        st.write("Verifique se a aba 'Treina-turma' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()