import streamlit as st
import pandas as pd
import tempfile
import os
from utils.data_utils import process_excel_file, SHEET_CONFIG

def render_upload_excel():
    st.subheader("Upload e Processamento de Novo Arquivo Excel")
    
    # Upload do arquivo Excel
    uploaded_file = st.file_uploader("Selecione um arquivo Excel", type=["xlsx"])
    
    if uploaded_file:
        try:
            # Cria um arquivo temporário com nome único
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
                tmp.write(uploaded_file.getbuffer())
                temp_file_path = tmp.name
            
            # Processa o arquivo
            processed_data = process_excel_file(temp_file_path)
            
            # Exibe as abas encontradas
            st.write("Abas encontradas no arquivo:", list(processed_data.keys()))
            
            # Seleção da aba para visualização
            selected_sheet = st.selectbox("Selecione uma aba para visualizar", list(processed_data.keys()))
            
            if selected_sheet:
                df = processed_data[selected_sheet]
                
                # Remove colunas 'Unnamed: X' ou renomeadas como 'Coluna_X'
                df = df.loc[:, ~df.columns.str.startswith('Coluna_')]
                
                # Exibe colunas e tipos de dados
                st.write("Colunas encontradas:", df.columns.tolist())
                st.write("Tipos de dados das colunas:", df.dtypes.to_dict())
                
                # Exibe amostra de todas as colunas (primeiras 5 linhas)
                st.write("Amostra dos dados (primeiras 5 linhas):")
                st.dataframe(df.head(5))
                
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
                            st.dataframe(filtered_df)
                    else:
                        st.dataframe(df)
                else:
                    st.dataframe(df)
        
        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {str(e)}")
            st.write("Verifique se o arquivo contém as abas e colunas esperadas conforme a configuração.")
        
        finally:
            # Tenta remover o arquivo temporário
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                st.warning(f"Não foi possível remover o arquivo temporário {temp_file_path}: {str(e)}")