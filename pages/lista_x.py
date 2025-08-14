import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_boolean_columns

def render_lista_x():
    st.subheader("Lista X")
    
    try:
        df = load_excel('Lista X')
        
        # Colunas esperadas
        expected_columns = [
            'Cidade', 'Não Informou a estrutura do posto', 'Com Pendência na estrutura do posto',
            'Sem pendência na estrutura do posto', 'Sanou pendências indicadas',
            'Ag. Visita técnica', 'Parecer da visita técnica', 'Realizou Treinamento',
            'Ag. Publicação no Diário Oficial Estado', 'Publicado no Diário Oficial do Estado',
            'Aguardando instalação', 'instalado'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes: {', '.join(missing_columns)}")

        # Tratar colunas booleanas
        bool_columns = [
            'Não Informou a estrutura do posto', 'Com Pendência na estrutura do posto',
            'Sem pendência na estrutura do posto', 'Sanou pendências indicadas',
            'Ag. Visita técnica', 'Realizou Treinamento',
            'Ag. Publicação no Diário Oficial Estado', 'Publicado no Diário Oficial do Estado',
            'Aguardando instalação', 'instalado'
        ]
        df = parse_boolean_columns(df, bool_columns)

        # Exibir tabela
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Lista X: {str(e)}")
        st.stop()