import streamlit as st
import pandas as pd
import os
from utils.data_utils import load_excel, process_sheet_data

# Caminho para o arquivo de cache
CACHE_FILE = "informacoes_gerais.xlsx"

def load_and_process_data():
    """Carrega e processa dados da aba 'Informações' do Excel original."""
    try:
        # Carrega e processa a aba 'Informações'
        df = load_excel('Informações')
        df = process_sheet_data(df, 'Informações')
        
        # Exibe colunas encontradas e tipos de dados para depuração
        st.write("Colunas encontradas na aba 'Informações':", df.columns.tolist())
        st.write("Tipos de dados das colunas:", df.dtypes.to_dict())
        
        # Exibe amostra de colunas potencialmente problemáticas
        for col in ['E-mail chefe de posto', 'PENDÊNCIA P/ VISITA TÉCNICA', 'Código do Posto']:
            if col in df.columns:
                st.write(f"Amostra dos dados na coluna '{col}' (primeiras 10 linhas):")
                st.write(df[col].head(10).tolist())
        
        # Salva os dados processados no arquivo de cache
        df.to_excel(CACHE_FILE, index=False, engine='openpyxl')
        
        return df
    
    except Exception as e:
        st.error(f"Erro ao processar a aba Informações: {str(e)}")
        st.write("Verifique se a aba 'Informações' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()

@st.cache_data
def load_cached_data():
    """Carrega os dados do arquivo de cache informacoes_gerais.xlsx."""
    try:
        df = pd.read_excel(CACHE_FILE, engine='openpyxl')
        # Reaplica processamento para garantir consistência
        df = process_sheet_data(df, 'Informações')
        return df
    except Exception as e:
        st.warning(f"Erro ao carregar o arquivo de cache {CACHE_FILE}: {str(e)}")
        st.write("Carregando dados do arquivo original...")
        return load_and_process_data()

def render_informacoes():
    st.subheader("Informações")
    
    # Botão de atualização
    if st.button("Atualizar Dados"):
        st.write("Atualizando dados a partir do arquivo original...")
        df = load_and_process_data()
        st.session_state['data'] = df
        st.success("Dados atualizados com sucesso!")
    else:
        # Verifica se o arquivo de cache existe
        if os.path.exists(CACHE_FILE):
            df = load_cached_data()
        else:
            st.write("Arquivo de cache não encontrado. Carregando dados do arquivo original...")
            df = load_and_process_data()
        
        st.session_state['data'] = df
    
    # Carrega o DataFrame da sessão
    df = st.session_state.get('data')
    
    if df is None:
        st.error("Nenhum dado carregado. Tente atualizar os dados.")
        st.stop()
    
    # Filtro por cidade
    cities = df['Cidade'].sort_values().unique().tolist()
    selected_city = st.selectbox("Selecione uma Cidade", [''] + cities, key="city_select")

    if selected_city:
        filtered_df = df[df['Cidade'] == selected_city]
        if filtered_df.empty:
            st.warning("Nenhum dado encontrado para a cidade selecionada.")
        else:
            st.dataframe(filtered_df)
    else:
        st.dataframe(df)