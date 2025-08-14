import streamlit as st
import pandas as pd
import os
from utils.data_utils import load_excel, parse_date_columns

# Caminho para o arquivo de cache
CACHE_FILE = "informacoes_gerais.xlsx"

def load_and_process_data():
    """Carrega e processa dados da aba 'Informações' do Excel original."""
    try:
        # Carrega a aba 'Informações' do arquivo original
        df = load_excel('Informações')
        
        # Colunas esperadas
        expected_columns = [
            'data/hora', 'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
            'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
            'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
            'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
            'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura',
            'PENDÊNCIA P/ VISITA TÉCNICA', 'Código do Posto'
        ]
        
        # Verifica colunas ausentes
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Informações': {', '.join(missing_columns)}")
        
        # Exibe colunas encontradas para depuração
        st.write("Colunas encontradas na aba 'Informações':", df.columns.tolist())
        
        # Exibe tipos de dados para depuração
        st.write("Tipos de dados das colunas:", df.dtypes.to_dict())
        
        # Exibe amostra das colunas problemáticas
        if 'PENDÊNCIA P/ VISITA TÉCNICA' in df.columns:
            st.write("Amostra dos dados na coluna 'PENDÊNCIA P/ VISITA TÉCNICA' (primeiras 10 linhas):")
            st.write(df['PENDÊNCIA P/ VISITA TÉCNICA'].head(10).tolist())
        if 'Código do Posto' in df.columns:
            st.write("Amostra dos dados na coluna 'Código do Posto' (primeiras 10 linhas):")
            st.write(df['Código do Posto'].head(10).tolist())
        
        # Converte colunas de texto para string, tratando valores nulos e não-textuais
        string_columns = [
            'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
            'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
            'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
            'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
            'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura',
            'PENDÊNCIA P/ VISITA TÉCNICA', 'Código do Posto'
        ]
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '').replace('nan', '')
        
        # Converte a coluna de data/hora
        if 'data/hora' in df.columns:
            df['data/hora'] = pd.to_datetime(df['data/hora'], format='%d/%m/%Y %H:%M', errors='coerce')
        else:
            st.warning("Coluna 'data/hora' não encontrada na aba 'Informações'.")
        
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
        # Reaplica conversão de data/hora para garantir consistência
        if 'data/hora' in df.columns:
            df['data/hora'] = pd.to_datetime(df['data/hora'], errors='coerce')
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