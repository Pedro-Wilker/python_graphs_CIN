import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_lista_x():
    st.subheader("Lista X", icon=":material/list:")
    
    try:
        raw_df = load_excel('Lista X')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Lista X')
        
        expected_columns = [
            'Cidade', 'Não Informou a estrutura do posto', 'Com Pendência na estrutura do posto',
            'Sem pendência na estrutura do posto', 'Sanou pendências indicadas', 'Ag. Visita técnica',
            'Parecer da visita técnica', 'Realizou Treinamento', 
            'Ag. Publicação no Diário Oficial Estado', 'Publicado no Diário Oficial do Estado',
            'Aguardando instalação', 'instalado'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Lista X': {', '.join(missing_columns)}")
            st.write("Colunas disponíveis:", df.columns.tolist())
        
        if 'Parecer da visita técnica' in df.columns:
            st.write("Valores únicos em 'Parecer da visita técnica':", df['Parecer da visita técnica'].unique().tolist())
        
        st.write("Amostra dos dados (primeiras 5 linhas):")
        st.dataframe(df.head(5))
        
        st.subheader("Tabela Completa")
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"Erro ao processar a aba Lista X: {str(e)}")
        st.write("Verifique se a aba 'Lista X' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()