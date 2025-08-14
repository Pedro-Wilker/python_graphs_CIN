import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_date_columns

def render_visitas_realizadas():
    st.subheader("Visitas Realizadas")
    
    try:
        df = load_excel('Visitas Realizadas')
        
        # Colunas esperadas
        expected_columns = [
            'CIDADE', 'DATA DE ANÁLISE', 'DATA DA VISITA TÉCNICA',
            'ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS?'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes: {', '.join(missing_columns)}")

        # Converter colunas de datas
        date_cols = ['DATA DE ANÁLISE', 'DATA DA VISITA TÉCNICA']
        df = parse_date_columns(df, date_cols)

        # Exibir tabela principal
        st.dataframe(df)

        # Sub-tabela Subtotal
        st.subheader("Subtotal")
        total_visits = len(df)
        approved_visits = len(df[df['PARECER DA VISITA TÉCNICA'] == 'Aprovado']) if 'PARECER DA VISITA TÉCNICA' in df.columns else 0
        reproved_visits = len(df[df['PARECER DA VISITA TÉCNICA'] == 'Reprovado']) if 'PARECER DA VISITA TÉCNICA' in df.columns else 0
        
        subtotal_df = pd.DataFrame({
            'Métrica': ['Total de visitas', 'Visitas aprovadas', 'Visitas reprovadas'],
            'Quantidade': [total_visits, approved_visits, reproved_visits]
        })
        st.dataframe(subtotal_df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Visitas Realizadas: {str(e)}")
        st.stop()