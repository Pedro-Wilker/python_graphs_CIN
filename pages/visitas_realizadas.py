import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_visitas_realizadas():  # Função deve ser render_visitas_realizadas
    st.markdown("""
        <h3>Visitas Realizadas <span class="material-icons" style="vertical-align: middle; color: #004aad;">check_circle</span></h3>
    """, unsafe_allow_html=True)
    
    try:
        df = load_excel('Visitas Realizadas')
        if df.empty:
            st.error("Nenhum dado carregado para a aba 'Visitas Realizadas'. Verifique o arquivo Excel.")
            return
        
        df = process_sheet_data(df, 'Visitas Realizadas')
        
        expected_columns = [
            'CIDADE', 
            'DATA DE ANÁLISE', 
            'DATA DA VISITA TÉCNICA', 
            'ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS?'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Visitas Realizadas': {', '.join(missing_columns)}")
        
        st.markdown("### Dados de Visitas Realizadas")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao processar a aba Visitas Realizadas: {str(e)}")
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está no diretório correto.
        - Confirme se a aba 'Visitas Realizadas' existe no arquivo Excel.
        - Assegure-se de que as colunas esperadas estão presentes e formatadas corretamente.
        """)