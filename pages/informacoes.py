import streamlit as st
import pandas as pd
import os
from utils.data_utils import load_excel, process_sheet_data

CACHE_FILE = "informacoes_gerais.xlsx"

@st.cache_data
def load_and_process_informacoes():
    """Carrega e processa a aba Informações com caching."""
    try:
        raw_df = load_excel('Informações')
        st.write("Colunas brutas no Excel:", raw_df.columns.tolist())
        st.write("Tipos de dados brutos:", raw_df.dtypes.to_dict())
        
        df = process_sheet_data(raw_df, 'Informações')
        
        # Limpeza adicional
        if 'PENDÊNCIA P/ VISITA TÉCNICA' in df.columns:
            df['PENDÊNCIA P/ VISITA TÉCNICA'] = df['PENDÊNCIA P/ VISITA TÉCNICA'].str.replace('\n', ' ', regex=False).str.strip()
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].str.replace('\n', ' ', regex=False).str.strip()
        
        st.write("Colunas processadas:", df.columns.tolist())
        st.write("Tipos de dados processados:", df.dtypes.to_dict())
        if 'PENDÊNCIA P/ VISITA TÉCNICA' in df.columns:
            st.write("Valores únicos em 'PENDÊNCIA P/ VISITA TÉCNICA':", df['PENDÊNCIA P/ VISITA TÉCNICA'].unique().tolist())
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            st.write("Valores únicos em 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA':", df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].unique().tolist())
        
        df.to_excel(CACHE_FILE, index=False, engine='openpyxl')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Informações: {str(e)}")
        st.stop()

@st.cache_data
def load_cached_data(_file_path=CACHE_FILE):
    """Carrega dados do cache."""
    try:
        df = pd.read_excel(_file_path, engine='openpyxl')
        df = process_sheet_data(df, 'Informações')
        
        # Limpeza adicional
        if 'PENDÊNCIA P/ VISITA TÉCNICA' in df.columns:
            df['PENDÊNCIA P/ VISITA TÉCNICA'] = df['PENDÊNCIA P/ VISITA TÉCNICA'].str.replace('\n', ' ', regex=False).str.strip()
        if 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA' in df.columns:
            df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = df['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'].str.replace('\n', ' ', regex=False).str.strip()
        
        return df
    except Exception as e:
        st.warning(f"Erro ao carregar o cache {_file_path}: {str(e)}")
        return load_and_process_informacoes()

def render_informacoes():
    st.subheader("Informações", icon=":material/info:")
    
    st.markdown("""
        <style>
        .search-container {
            border: 1px solid #004aad;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f0f2f6;
        }
        .search-container h3 {
            color: #004aad;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    expected_columns = [
        'data/hora', 'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
        'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
        'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
        'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
        'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura',
        'PENDÊNCIA P/ VISITA TÉCNICA', 'Código do Posto', 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
    ]
    
    if st.button("Atualizar Dados", icon=":material/refresh:"):
        st.write("Atualizando dados a partir do arquivo original...")
        df = load_and_process_informacoes()
        st.session_state['data_informacoes'] = df
        st.success("Dados atualizados com sucesso!")
    else:
        if os.path.exists(CACHE_FILE):
            df = load_cached_data()
        else:
            st.write("Arquivo de cache não encontrado. Carregando dados do arquivo original...")
            df = load_and_process_informacoes()
        
        st.session_state['data_informacoes'] = df
    
    df = st.session_state.get('data_informacoes')
    
    if df is None:
        st.error("Nenhum dado carregado. Tente atualizar os dados.")
        st.stop()
    
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Informações': {', '.join(missing_columns)}")
    
    with st.container():
        st.markdown('<div class="search-container"><h3>Buscar Informações</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            search_city = st.selectbox("Cidade", [''] + sorted(df['Cidade'].unique().tolist()), key="search_city")
            search_chief = st.text_input("Nome do Chefe de Posto", key="search_chief")
            search_email = st.text_input("E-mail do Chefe de Posto", key="search_email")
        
        with col2:
            search_secretary = st.text_input("Nome do Secretário/Coordenador", key="search_secretary")
            search_address = st.text_input("Endereço do Posto", key="search_address")
            search_pendency = st.text_input("Pendência p/ Visita Técnica", key="search_pendency")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    filtered_df = df
    if search_city:
        filtered_df = filtered_df[filtered_df['Cidade'].str.contains(search_city, case=False, na=False)]
    if search_chief:
        filtered_df = filtered_df[filtered_df['Nome do chefe de posto'].str.contains(search_chief, case=False, na=False)]
    if search_email:
        filtered_df = filtered_df[filtered_df['E-mail chefe de posto'].str.contains(search_email, case=False, na=False)]
    if search_secretary:
        filtered_df = filtered_df[filtered_df['Nome do Secretário/Coordenador'].str.contains(search_secretary, case=False, na=False)]
    if search_address:
        filtered_df = filtered_df[filtered_df['Endereço do Posto'].str.contains(search_address, case=False, na=False)]
    if search_pendency:
        filtered_df = filtered_df[filtered_df['PENDÊNCIA P/ VISITA TÉCNICA'].str.contains(search_pendency, case=False, na=False)]
    
    if filtered_df.empty:
        st.warning("Nenhum dado encontrado para os critérios de busca.")
    else:
        st.subheader("Resultados da Busca")
        st.dataframe(filtered_df, use_container_width=True)
    
    if not (search_city or search_chief or search_email or search_secretary or search_address or search_pendency):
        st.subheader("Tabela Completa")
        st.dataframe(df, use_container_width=True)