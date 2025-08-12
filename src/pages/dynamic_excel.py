import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import os
from math import ceil

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho para a pasta 'data'
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Garante que a pasta 'data' existe
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Função com cache para carregar dados do Excel
@st.cache_data
def load_excel_data(file, sheet_name):
    try:
        return pd.read_excel(file, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Erro ao carregar a aba {sheet_name}: {e}")
        logger.error(f"Erro ao carregar a aba {sheet_name}: {e}")
        return None

# Função para listar arquivos Excel na pasta 'data'
def list_local_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]
        return files
    except Exception as e:
        st.error(f"Erro ao listar arquivos na pasta 'data': {e}")
        logger.error(f"Erro ao listar arquivos na pasta 'data': {e}")
        return []

# Função para inferir e formatar o tipo de dado de uma coluna
def get_column_type(df, column):
    dtype = df[column].dtype
    sample = df[column].dropna().head(1).values
    if pd.api.types.is_datetime64_any_dtype(dtype) or (sample.size > 0 and isinstance(sample[0], pd.Timestamp)):
        return "Data (ex: dd/mm/yyyy)"
    elif pd.api.types.is_object_dtype(dtype):
        unique_values = df[column].dropna().unique()
        if set(unique_values).issubset({"Sim", "Não"}):
            return "Categórico (Sim/Não)"
        return "Categórico"
    elif pd.api.types.is_numeric_dtype(dtype):
        return "Numérico"
    return str(dtype)

# Função para exibir tabela com paginação
def display_paginated_table(df, sheet_name, page_size=10):
    total_rows = len(df)
    total_pages = ceil(total_rows / page_size)
    page_number = st.number_input(
        "Página",
        min_value=1,
        max_value=max(total_pages, 1),
        value=1,
        step=1,
        key=f"page_input_{sheet_name}"  # Chave única baseada no nome da aba
    )
    start_idx = (page_number - 1) * page_size
    end_idx = start_idx + page_size
    st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True)
    st.write(f"Página {page_number} de {total_pages} (Total de linhas: {total_rows})")

st.set_page_config(page_title="Análise Dinâmica", layout="wide")
st.title("Análise Dinâmica de Excel")

# Opção para carregar arquivo via upload ou pasta local
data_source = st.radio("Escolha a fonte do arquivo", ["Upload", "Pasta Local"])

# Inicializar file como None
file = None

if data_source == "Upload":
    uploaded_file = st.file_uploader("Carregue o arquivo Excel", type=["xlsx"])
    if uploaded_file:
        # Salvar o arquivo na pasta 'data'
        try:
            file_path = os.path.join(DATA_DIR, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Arquivo {uploaded_file.name} salvo na pasta 'data'.")
            logger.info(f"Arquivo {uploaded_file.name} salvo em {file_path}")
            file = file_path
        except Exception as e:
            st.error(f"Erro ao salvar o arquivo: {e}")
            logger.error(f"Erro ao salvar o arquivo: {e}")
            file = None
else:
    # Listar arquivos da pasta 'data'
    local_files = list_local_files()
    if local_files:
        selected_file = st.selectbox("Escolha o arquivo da pasta 'data'", local_files)
        file = os.path.join(DATA_DIR, selected_file)
    else:
        st.info("Nenhum arquivo Excel encontrado na pasta 'data'.")
        file = None

if file:
    try:
        xls = pd.ExcelFile(file)
        sheets = xls.sheet_names
        logger.info(f"Abas disponíveis: {sheets}")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo Excel: {e}")
        logger.error(f"Erro ao processar o arquivo Excel: {e}")
        sheets = []

    if sheets:
        # Exibir dados de todas as abas em sub-abas
        st.subheader("Dados do Arquivo Excel")
        tabs = st.tabs(sheets)  # Cria uma sub-aba para cada aba do Excel
        sheet_data = {}  # Armazena os DataFrames de cada aba
        for sheet_name, tab in zip(sheets, tabs):
            with tab:
                df = load_excel_data(file, sheet_name)
                if df is not None:
                    sheet_data[sheet_name] = df
                    st.write(f"Dados da aba: {sheet_name}")
                    display_paginated_table(df, sheet_name)  # Passa o nome da aba para a chave única
                else:
                    st.error(f"Não foi possível carregar os dados da aba {sheet_name}.")

        # Seleção de aba para análise detalhada
        st.subheader("Análise Detalhada")
        selected_sheet = st.selectbox("Escolha a aba para análise", sheets)
        if selected_sheet:
            # Verificar se o DataFrame já está em sheet_data, senão carregar
            df = sheet_data.get(selected_sheet)
            if df is None:
                df = load_excel_data(file, selected_sheet)
            if df is not None:
                columns = df.columns.tolist()
                selected_columns = st.multiselect("Escolha as colunas", columns)
                
                # Exibir tipos de dados das colunas selecionadas
                if selected_columns:
                    st.write("**Tipos de dados das colunas selecionadas:**")
                    for col in selected_columns:
                        col_type = get_column_type(df, col)
                        st.write(f"- {col}: {col_type}")
                
                # Seleção do tipo de gráfico
                graph_type = st.selectbox("Tipo de gráfico", ["Pizza", "Barras", "Linhas"])
                if selected_columns and graph_type:
                    logger.info(f"Aba selecionada: {selected_sheet}, Colunas: {selected_columns}, Gráfico: {graph_type}")
                    for col in selected_columns:
                        try:
                            if df[col].dtype == "object":  # Categórico
                                counts = df[col].value_counts().reset_index()
                                counts.columns = [col, "Contagem"]
                                if graph_type == "Pizza":
                                    fig = px.pie(counts, values="Contagem", names=col, title=f"Distribuição de {col}")
                                    st.plotly_chart(fig)
                                else:
                                    st.warning(f"Gráfico {graph_type} não suportado para dados categóricos.")
                            else:  # Numérico ou Data
                                if graph_type == "Barras":
                                    fig = px.bar(df, x=df.index, y=col, title=f"{col} por Índice")
                                    st.plotly_chart(fig)
                                elif graph_type == "Linhas":
                                    fig = px.line(df, x=df.index, y=col, title=f"{col} ao Longo do Tempo")
                                    st.plotly_chart(fig)
                                else:
                                    st.warning(f"Gráfico {graph_type} não suportado para dados numéricos.")
                        except Exception as e:
                            st.error(f"Erro ao gerar gráfico para a coluna {col}: {e}")
                            logger.error(f"Erro ao gerar gráfico para {col}: {e}")
                else:
                    st.info("Selecione pelo menos uma coluna e um tipo de gráfico.")
            else:
                st.error("Não foi possível carregar os dados da aba selecionada.")
    else:
        st.info("Nenhuma aba disponível no arquivo.")
else:
    st.info("Nenhum arquivo selecionado ou disponível.")