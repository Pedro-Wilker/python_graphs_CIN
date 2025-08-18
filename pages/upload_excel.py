import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data, SHEET_CONFIG

def render_upload_excel():
    st.markdown("""
        <h3>Dados do Arquivo Excel <span class="material-icons" style="vertical-align: middle; color: #004aad;">table_chart</span></h3>
    """, unsafe_allow_html=True)
    
    try:
        # Carregar todas as abas do arquivo padrão
        excel_file = r"C:\Users\re049227\Documents\pythonGraphs\ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"
        xls = pd.ExcelFile(excel_file, engine='openpyxl')
        sheets = xls.sheet_names
        
        st.markdown("### Abas Disponíveis")
        st.write("Abas encontradas no arquivo:", sheets)
        
        # Seleção da aba para visualização
        selected_sheet = st.selectbox("Selecione uma aba para visualizar", sheets, key="upload_excel_sheet")
        
        if selected_sheet:
            df = load_excel(selected_sheet)
            if df.empty:
                st.error(f"Nenhum dado carregado para a aba '{selected_sheet}'. Verifique o arquivo Excel.")
                return
            
            df = process_sheet_data(df, selected_sheet)
            
            # Remove colunas indesejadas
            df = df.loc[:, ~df.columns.str.startswith('Coluna_')]
            
            # Exibe colunas e tipos de dados
            st.markdown("### Colunas Encontradas")
            st.write("Colunas:", df.columns.tolist())
            st.write("Tipos de dados:", df.dtypes.to_dict())
            
            # Exibe amostra de dados
            st.markdown("### Amostra dos Dados (Primeiras 5 Linhas)")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Filtro por cidade, se disponível
            if 'Cidade' in df.columns or 'CIDADE' in df.columns:
                city_col = 'Cidade' if 'Cidade' in df.columns else 'CIDADE'
                cities = df[city_col].sort_values().unique().tolist()
                selected_city = st.selectbox("Selecione uma Cidade", [''] + cities, key="upload_city_select")
                
                if selected_city:
                    filtered_df = df[df[city_col] == selected_city]
                    if filtered_df.empty:
                        st.warning("Nenhum dado encontrado para a cidade selecionada.")
                    else:
                        st.markdown("### Dados Filtrados por Cidade")
                        st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.markdown("### Dados Completos")
                    st.dataframe(df, use_container_width=True)
            else:
                st.markdown("### Dados Completos")
                st.dataframe(df, use_container_width=True)
                
    except Exception as e:
        st.error(f"Erro ao processar o arquivo Excel: {str(e)}")
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está no diretório correto.
        - Confirme se as abas esperadas existem no arquivo Excel.
        - Assegure-se de que as colunas estão formatadas corretamente.
        """)