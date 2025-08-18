import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_treina_cidade():
    st.markdown("""
        <h3>Treina Cidade <span class="material-icons" style="vertical-align: middle; color: #004aad;">location_city</span></h3>
    """, unsafe_allow_html=True)
    
    try:
        df = load_excel('Treina-cidade')
        if df.empty:
            st.error("Nenhum dado carregado para a aba 'Treina-cidade'. Verifique o arquivo Excel.")
            return
        
        df = process_sheet_data(df, 'Treina-cidade')
        
        # Verificar colunas esperadas
        expected_columns = ['CIDADE', 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM', 'TURMA', 'REALIZOU TREINAMENTO?']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Treina-cidade': {', '.join(missing_columns)}")
        
        st.markdown("### Dados por Cidade de Treinamento")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao processar a aba Treina-cidade: {str(e)}")
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está no diretório correto.
        - Confirme se a aba 'Treina-cidade' existe no arquivo Excel.
        - Assegure-se de que as colunas esperadas estão presentes e formatadas corretamente.
        """)