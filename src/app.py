import streamlit as st
from utils.data_loader import load_and_process_data
from utils.aggregators import aggregate_data
from utils.filters import check_duplicates
from components.general_charts import render_general_charts
from components.individual_analysis import render_individual_tab
from components.comparison_cities import render_comparison_cities_tab
from components.comparison_dates import render_comparison_dates_tab

st.title("Análise das Produções de CIN das Cidades-Bahia")

# Carregar e processar dados
try:
    df, months = load_and_process_data("data/ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx")
    check_duplicates(df)
    df = aggregate_data(df, months)
    render_general_charts(df, months)
    tab1, tab2, tab3 = st.tabs(["Análise Individual", "Comparação de Cidades", "Comparação por Datas"])
    with tab1:
        render_individual_tab(df, months)
    with tab2:
        render_comparison_cities_tab(df, months)
    with tab3:
        render_comparison_dates_tab(df, months)
except Exception as e:
    st.error(f"Erro ao carregar o Excel: {str(e)}")
    st.write("Verifique se o arquivo 'ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx' está na raiz do projeto, possui a aba 'Produtividade' e contém as colunas esperadas no formato correto.")
    st.stop()