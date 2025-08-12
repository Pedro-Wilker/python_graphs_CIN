import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import os
import time

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Caminho para a pasta 'data'
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

# Função para listar arquivos Excel na pasta 'data'
def list_local_files():
    try:
        files = [f for f in os.listdir(DATA_DIR) if f.endswith('.xlsx')]
        return files
    except Exception as e:
        st.error(f"Erro ao listar arquivos na pasta 'data': {e}")
        logger.error(f"Erro ao listar arquivos na pasta 'data': {e}")
        return []

# Função para carregar dados de uma aba específica com cache
@st.cache_data
def load_excel_data(file_path, sheet_name):
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Erro ao carregar a aba {sheet_name}: {e}")
        logger.error(f"Erro ao carregar a aba {sheet_name}: {e}")
        return None

# Função para inferir o tipo de dado de uma coluna
def get_column_type(df, column):
    dtype = df[column].dtype
    sample = df[column].dropna().head(1).values
    if pd.api.types.is_datetime64_any_dtype(dtype) or (sample.size > 0 and isinstance(sample[0], pd.Timestamp)):
        return "Data"
    elif pd.api.types.is_object_dtype(dtype):
        unique_values = df[column].dropna().unique()
        if set(unique_values).issubset({"Sim", "Não"}):
            return "Categórico (Sim/Não)"
        return "Categórico"
    elif pd.api.types.is_numeric_dtype(dtype):
        return "Numérico"
    return str(dtype)

# Função para gerar gráficos dinamicamente
def generate_graphs(df):
    graphs = []
    columns = df.columns.tolist()
    date_column = None

    # Identificar coluna de data para usar como animation_frame
    for col in columns:
        if get_column_type(df, col) == "Data":
            date_column = col
            break

    # Gerar gráficos para colunas numéricas
    for col in columns:
        col_type = get_column_type(df, col)
        if col_type == "Numérico":
            if date_column:
                graphs.append({
                    "type": "line",
                    "title": f"{col} ao Longo do Tempo",
                    "func": lambda df, col=col: px.line(
                        df, x=date_column, y=col, title=f"{col} ao Longo do Tempo", animation_frame=date_column
                    )
                })
            else:
                graphs.append({
                    "type": "bar",
                    "title": f"{col} por Índice",
                    "func": lambda df, col=col: px.bar(
                        df, x=df.index, y=col, title=f"{col} por Índice"
                    )
                })

    # Gerar gráficos para colunas categóricas
    for col in columns:
        col_type = get_column_type(df, col)
        if col_type in ["Categórico", "Categórico (Sim/Não)"]:
            graphs.append({
                "type": "pie",
                "title": f"Distribuição de {col}",
                "func": lambda df, col=col: px.pie(
                    df[col].value_counts().reset_index(),
                    values="count",
                    names=col,
                    title=f"Distribuição de {col}",
                    animation_frame=date_column if date_column else None
                )
            })

    return graphs

st.set_page_config(page_title="Dashboard Slideshow", layout="wide")
st.title("Dashboard Slideshow Automático")

# Botão de tela cheia com estilo CSS
st.markdown(
    """
    <style>
    .fullscreen-button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 16px;
    }
    .fullscreen-button:hover {
        background-color: #45a049;
    }
    </style>
    <button class="fullscreen-button" onclick="document.documentElement.requestFullscreen()">Tela Cheia</button>
    """,
    unsafe_allow_html=True
)

# Seleção de arquivo da pasta 'data'
local_files = list_local_files()
if local_files:
    selected_file = st.selectbox("Escolha o arquivo da pasta 'data'", local_files)
    file_path = os.path.join(DATA_DIR, selected_file)
else:
    st.info("Nenhum arquivo Excel encontrado na pasta 'data'.")
    st.stop()

# Carregar abas disponíveis
try:
    xls = pd.ExcelFile(file_path)
    sheets = xls.sheet_names
    logger.info(f"Abas disponíveis: {sheets}")
except Exception as e:
    st.error(f"Erro ao processar o arquivo Excel: {e}")
    logger.error(f"Erro ao processar o arquivo Excel: {e}")
    st.stop()

# Seleção de aba
if sheets:
    selected_sheet = st.selectbox("Escolha a aba para análise", sheets)
else:
    st.info("Nenhuma aba disponível no arquivo.")
    st.stop()

# Carregar dados da aba selecionada
df = load_excel_data(file_path, selected_sheet)
if df is None:
    st.error(f"Não foi possível carregar os dados da aba {selected_sheet}.")
    st.stop()

# Gerar gráficos dinamicamente
graphs = generate_graphs(df)
if not graphs:
    st.info("Nenhuma coluna adequada para gerar gráficos.")
    st.stop()

# Inicializar estado da sessão
if 'current_slide' not in st.session_state:
    st.session_state.current_slide = 0
if 'last_update' not in st.session_state:
    st.session_state.last_update = 0

# Configuração do slideshow
SLIDE_DURATION = 120  # 2 minutos em segundos

# Botões para navegação manual
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    if st.button("Anterior"):
        st.session_state.current_slide = (st.session_state.current_slide - 1) % len(graphs)
        st.session_state.last_update = time.time()
with col2:
    st.write(f"Slide {st.session_state.current_slide + 1} de {len(graphs)}")
with col3:
    if st.button("Próximo"):
        st.session_state.current_slide = (st.session_state.current_slide + 1) % len(graphs)
        st.session_state.last_update = time.time()

# Verificar se é hora de avançar automaticamente
current_time = time.time()
if current_time - st.session_state.last_update >= SLIDE_DURATION:
    st.session_state.current_slide = (st.session_state.current_slide + 1) % len(graphs)
    st.session_state.last_update = current_time
    st.rerun()

# Exibir o gráfico atual
current_graph = graphs[st.session_state.current_slide]
try:
    fig = current_graph["func"](df)
    st.plotly_chart(fig, use_container_width=True)
    logger.info(f"Exibindo gráfico: {current_graph['title']}")
except Exception as e:
    st.error(f"Erro ao gerar o gráfico {current_graph['title']}: {e}")
    logger.error(f"Erro ao gerar o gráfico {current_graph['title']}: {e}")