import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_utils import load_excel, EXCEL_FILE
import time

@st.cache_data
def load_and_process_produtividade(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Produtividade com caching otimizado."""
    try:
        df = load_excel('Produtividade', _file_path)
        if df.empty:
            st.warning("Nenhum dado disponível para a aba 'Produtividade'.")
            return pd.DataFrame()
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Verificar colunas necessárias
        required_columns = ['CIDADE', 'ABRIL']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Colunas ausentes na aba 'Produtividade': {', '.join(missing_columns)}")
            return pd.DataFrame()
        
        # Tratar CIDADE e ABRIL
        df['CIDADE'] = df['CIDADE'].astype(str).str.strip().replace('nan', '')
        df['ABRIL'] = pd.to_numeric(df['ABRIL'], errors='coerce').fillna(0.0)
        df = df[df['CIDADE'].notna() & (df['CIDADE'] != '') & (df['CIDADE'] != 'TOTAL')]
        
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Produtividade: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_and_process_generic(sheet_name, _file_path=EXCEL_FILE):
    """Carrega e processa outras abas do Excel de forma genérica."""
    try:
        df = load_excel(sheet_name, _file_path)
        if df.empty:
            return pd.DataFrame()
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Tratar CIDADE, se presente
        if 'CIDADE' in df.columns:
            df['CIDADE'] = df['CIDADE'].astype(str).str.strip().replace('nan', '')
            df = df[df['CIDADE'].notna() & (df['CIDADE'] != '')]
        
        # Converter colunas potencialmente numéricas
        for col in df.select_dtypes(include=['object']).columns:
            if col != 'CIDADE':
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        st.warning(f"Erro ao processar a aba {sheet_name}: {str(e)}")
        return pd.DataFrame()

def generate_charts(df, sheet_name, limite_cidades):
    """Gera gráficos para a aba especificada."""
    charts = []
    if limite_cidades != "Sem Limites" and sheet_name != 'Produtividade':
        try:
            limit = int(limite_cidades)
            df_grafico = df.head(limit)
        except ValueError:
            st.error("Erro: Limite de cidades inválido.")
            return charts
    else:
        df_grafico = df.copy()
    
    # Gráficos genéricos para outras abas
    if sheet_name in ['Instalados', 'Ag_Instalacao', 'Ag. Visita', 'Ag_info_prefeitura']:
        if not df_grafico.empty and 'CIDADE' in df_grafico.columns:
            numeric_cols = df_grafico.select_dtypes(include=['int64', 'float64']).columns
            if numeric_cols.size > 0:
                y_col = numeric_cols[0]  # Usar a primeira coluna numérica
                fig_bar = px.bar(
                    df_grafico,
                    x='CIDADE',
                    y=y_col,
                    title=f'{sheet_name}: Dados por Cidade',
                    height=400,
                    color_discrete_sequence=['#004aad']
                )
                fig_bar.update_traces(texttemplate='%{y}', textposition='outside')
                fig_bar.update_layout(margin=dict(t=50, b=50, l=50, r=50))
                charts.append(fig_bar)
    
    # Gráficos específicos para Produtividade
    if sheet_name == 'Produtividade':
        # Gráfico 1: Análise Individual para Nova Soure (Abril)
        df_nova_soure = df_grafico[df_grafico['CIDADE'] == 'Nova Soure']
        if not df_nova_soure.empty:
            abril_data = df_nova_soure[['CIDADE', 'ABRIL']].copy()
            abril_data['Produção'] = abril_data['ABRIL']
            if abril_data['Produção'].sum() > 0:
                fig_nova_soure = px.bar(
                    abril_data,
                    x='CIDADE',
                    y='Produção',
                    title='Produtividade: Nova Soure (Abril/2025)',
                    height=400,
                    color_discrete_sequence=['#004aad']
                )
                fig_nova_soure.update_traces(texttemplate='%{y}', textposition='outside')
                fig_nova_soure.update_layout(margin=dict(t=50, b=50, l=50, r=50))
                charts.append(fig_nova_soure)
        
        # Gráfico 2: Comparação por Cidade (Andaraí, Dom Macedo Costa, Nova Soure, Piritiba)
        cidades_comparacao = ['Andaraí', 'Dom Macedo Costa', 'Nova Soure', 'Piritiba']
        df_comparacao = df_grafico[df_grafico['CIDADE'].isin(cidades_comparacao)][['CIDADE', 'ABRIL']].copy()
        df_comparacao['Produção'] = df_comparacao['ABRIL']
        if not df_comparacao.empty and df_comparacao['Produção'].sum() > 0:
            fig_comparacao = px.bar(
                df_comparacao,
                x='CIDADE',
                y='Produção',
                title='Produtividade: Comparação por Cidade (Abril/2025)',
                height=400,
                color='CIDADE',
                barmode='group',
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig_comparacao.update_traces(texttemplate='%{y}', textposition='outside')
            fig_comparacao.update_layout(margin=dict(t=50, b=50, l=50, r=50))
            charts.append(fig_comparacao)
    
    return charts

def render_dashboard_central(uploaded_file=None):
    st.markdown("""
        <h2>Dashboard Central <span class="material-icons" style="vertical-align: middle; color: #004aad;">dashboard</span></h2>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    abas = ['Instalados', 'Ag_Instalacao', 'Ag. Visita', 'Ag_info_prefeitura', 'Produtividade']
    
    # Seletor de limite de cidades
    limite_cidades = st.selectbox(
        "Limitar número de cidades no dashboard (exclui Produtividade)",
        ["2", "5", "10", "Sem Limites"],
        index=3,
        key="limite_cidades"
    )
    
    # Carregar e processar a aba Produtividade
    df_produtividade = load_and_process_produtividade(file_path)
    charts = []
    if not df_produtividade.empty:
        charts.extend(generate_charts(df_produtividade, 'Produtividade', limite_cidades))
    else:
        st.warning("Nenhum dado válido na aba 'Produtividade'. Gráficos de produtividade não serão exibidos.")
    
    # Carregar outras abas apenas se necessário
    for aba in abas:
        if aba != 'Produtividade':
            df = load_and_process_generic(aba, file_path)
            if not df.empty:
                charts.extend(generate_charts(df, aba, limite_cidades))
    
    if not charts:
        st.error("Nenhum gráfico gerado. Verifique os dados no arquivo Excel.")
        return
    
    # Inicializar estado do slideshow
    if 'chart_index' not in st.session_state:
        st.session_state['chart_index'] = 0
    
    # Controles manuais
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("Anterior", key="prev"):
            st.session_state['chart_index'] = (st.session_state['chart_index'] - 1) % len(charts)
    with col2:
        if st.button("Próximo", key="next"):
            st.session_state['chart_index'] = (st.session_state['chart_index'] + 1) % len(charts)
    with col3:
        auto_play = st.checkbox("Auto-play", value=False, key="auto_play")
    
    # Exibir gráfico atual
    slideshow_placeholder = st.empty()
    with slideshow_placeholder.container():
        st.plotly_chart(charts[st.session_state['chart_index']], use_container_width=True)
    
    # Auto-play com temporizador
    if auto_play:
        time_placeholder = st.empty()
        for i in range(5, 0, -1):
            time_placeholder.write(f"Próximo gráfico em {i} segundos...")
            time.sleep(1)
        st.session_state['chart_index'] = (st.session_state['chart_index'] + 1) % len(charts)
        st.rerun()

if __name__ == "__main__":
    render_dashboard_central()