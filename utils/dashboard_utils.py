import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import plotly.express as px
from python_graphs_CIN.utils.data_utils import load_excel, process_sheet_data, SHEET_CONFIG, EXCEL_FILE
from python_graphs_CIN.pages.ag_info_prefeitura import generate_ag_info_prefeitura_dashboard
from python_graphs_CIN.pages.ag_instalacao import generate_ag_instalacao_dashboards
from python_graphs_CIN.pages.ag_visita import generate_ag_visita_dashboards
from python_graphs_CIN.pages.servicos_a_revisar import generate_servicos_a_revisar_dashboards

@st.cache_data
def load_and_process_ag_info_prefeitura(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag_info_prefeitura com caching."""
    try:
        raw_df = load_excel('Ag_info_prefeitura', _file_path)
        if raw_df.empty:
            return pd.DataFrame()
        df = process_sheet_data(raw_df, 'Ag_info_prefeitura')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_info_prefeitura: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_and_process_ag_instalacao(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag_Instalacao com caching."""
    try:
        raw_df = load_excel('Ag_Instalacao', _file_path)
        if raw_df.empty:
            return pd.DataFrame()
        df = process_sheet_data(raw_df, 'Ag_Instalacao')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_Instalacao: {str(e)}")
        return pd.DataFrame()

@st.cache_data
def load_and_process_ag_visita(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag. Visita com caching."""
    try:
        raw_df = load_excel('Ag. Visita', _file_path)
        if raw_df.empty:
            return pd.DataFrame()
        df = process_sheet_data(raw_df, 'Ag. Visita')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag. Visita: {str(e)}")
        return pd.DataFrame()

ARQUIVO_SERVICOS = os.path.join(os.path.dirname(__file__), '..', 'revisarservicos.txt')

def parse_data_linha(linha):
    """Parseia uma linha do arquivo revisarservicos.txt."""
    try:
        if linha.strip().lower().startswith('serviço | orgao | tempo | data ultima publicacao'):
            return None
        partes = [p.strip() for p in linha.split('|')]
        servico = partes[0] if len(partes) >= 1 else ''
        orgao = ''
        tempo = 0
        data_formatada = ''
        if len(partes) >= 2:
            segundo_campo = partes[1]
            match_tempo = re.search(r'(\d+)$', segundo_campo)
            if match_tempo:
                tempo = int(match_tempo.group(1))
                orgao = segundo_campo[:match_tempo.start()].strip()
            else:
                orgao = segundo_campo
        if len(partes) >= 3:
            try:
                tempo = int(re.findall(r'\d+', partes[2])[0]) if re.findall(r'\d+', partes[2]) else tempo
            except:
                pass
        if len(partes) >= 4 and partes[3]:
            data_raw = partes[3]
            match = re.match(r'(\d{1,2})\s*de\s*(\w+)\s*(?:de\s*)?(\d{4})(?:\s*às\s*(\d{2}:\d{2}))?', data_raw, re.IGNORECASE)
            if match:
                groups = match.groups()
                dia = groups[0]
                mes = groups[1].lower()
                ano = groups[2]
                hora = groups[3] if len(groups) > 3 else None
                meses = {
                    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 'maio': '05', 'junho': '06',
                    'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
                }
                mes_num = meses.get(mes, '01')
                data_formatada = f"{dia.zfill(2)}/{mes_num}/{ano}" + (f" {hora}" if hora else "")
            else:
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%Y-%m-%d']:
                    try:
                        data_dt = pd.to_datetime(data_raw, format=fmt, errors='coerce')
                        if pd.notna(data_dt):
                            data_formatada = data_dt.strftime('%d/%m/%Y')
                            break
                    except:
                        continue
        return {'SERVIÇO': servico, 'ORGAO': orgao, 'TEMPO': tempo, 'DATA ULTIMA PUBLICAÇÃO': data_formatada}
    except:
        return None

def carregar_dados_servicos():
    """Carrega dados do arquivo revisarservicos.txt."""
    try:
        with open(ARQUIVO_SERVICOS, encoding='utf-8') as f:
            linhas = f.readlines()
        dados = [parse_data_linha(linha) for linha in linhas if linha.strip() and parse_data_linha(linha)]
        df = pd.DataFrame(dados)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar revisarservicos.txt: {str(e)}")
        return pd.DataFrame()

def atualizar_tempo_servicos(df):
    """Atualiza a coluna TEMPO com base na data atual."""
    hoje = datetime.now()
    for idx, row in df.iterrows():
        data_str = row['DATA ULTIMA PUBLICAÇÃO']
        if data_str and data_str.strip():
            try:
                for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y']:
                    try:
                        data_dt = datetime.strptime(data_str, fmt)
                        dias = (hoje.date() - data_dt.date()).days
                        df.at[idx, 'TEMPO'] = dias
                        break
                    except ValueError:
                        continue
            except:
                df.at[idx, 'TEMPO'] = 0
        else:
            df.at[idx, 'TEMPO'] = 0
    return df

@st.cache_data
def load_and_process_produtividade(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Produtividade com caching."""
    try:
        raw_df = load_excel('Produtividade', _file_path)
        if raw_df.empty:
            return pd.DataFrame(), []
        df = process_sheet_data(raw_df, 'Produtividade')
        possible_months = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        months = [m for m in possible_months if m in df.columns]
        df = df[df['CIDADE'].notna() & (df['CIDADE'] != '') & (df['CIDADE'] != 'TOTAL')]
        df = df[df['PREFEITURAS DE'].notna() & (df['PREFEITURAS DE'] != '')]
        duplicate_cities = df[df['CIDADE'].duplicated(keep=False)]['CIDADE'].unique()
        if len(duplicate_cities) > 0:
            agg_dict = {month: 'sum' for month in months}
            agg_dict.update({
                'REALIZOU TREINAMENTO?': 'first',
                'DATA DA INSTALAÇÃO': 'min',
                'DATA DO INÍCIO ATEND.': 'min',
                'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO': 'min',
                'PERÍODO PREVISTO DE TREINAMENTO_FIM': 'min',
                'PREFEITURAS DE': 'first'
            })
            df = df.groupby('CIDADE').agg(agg_dict).reset_index()
        return df, months
    except Exception as e:
        st.error(f"Erro ao processar a aba Produtividade: {str(e)}")
        return pd.DataFrame(), []

def generate_produtividade_dashboard(df, months, limite_cidades="Sem Limites"):
    """Gera gráficos para a aba 'Produtividade'."""
    if df.empty or not months:
        return []
    
    df_plot = df.head(limite_cidades) if isinstance(limite_cidades, int) else df
    figs = []
    
    # Gráfico 1: Total de atendimentos por mês
    df_melted = df_plot.melt(id_vars=['CIDADE'], value_vars=months, var_name='Mês', value_name='Atendimentos')
    df_melted = df_melted[df_melted['Atendimentos'] > 0]
    if not df_melted.empty:
        fig1 = px.bar(
            df_melted,
            x='Mês',
            y='Atendimentos',
            color='CIDADE',
            title='Total de Atendimentos por Mês',
            text='Atendimentos',
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig1.update_traces(textposition='outside')
        fig1.update_layout(xaxis_title="Mês", yaxis_title="Número de Atendimentos")
        figs.append(fig1)
    
    # Gráfico 2: Cidades com treinamento realizado
    treinamento_counts = df_plot['REALIZOU TREINAMENTO?'].value_counts().reset_index()
    treinamento_counts.columns = ['Treinamento', 'Quantidade']
    treinamento_counts['Treinamento'] = treinamento_counts['Treinamento'].map({True: 'Realizado', False: 'Não Realizado'})
    fig2 = px.pie(
        treinamento_counts,
        values='Quantidade',
        names='Treinamento',
        title='Cidades com Treinamento Realizado',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig2.update_traces(textinfo='percent+label')
    figs.append(fig2)
    
    # Gráfico 3: Atendimentos por cidade
    df_sum = df_plot[['CIDADE'] + months].copy()
    df_sum['Total Atendimentos'] = df_sum[months].sum(axis=1)
    fig3 = px.bar(
        df_sum,
        x='CIDADE',
        y='Total Atendimentos',
        title='Total de Atendimentos por Cidade',
        text='Total Atendimentos',
        color='CIDADE',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig3.update_traces(textposition='outside')
    fig3.update_layout(showlegend=False, xaxis_title="Cidade", yaxis_title="Total de Atendimentos")
    figs.append(fig3)
    
    return figs

def render_dashboard_central(uploaded_file=None):
    """Renderiza o dashboard central com todas as abas."""
    st.markdown("""
        <h2>Dashboard Central <span class="material-icons" style="vertical-align: middle; color: #004aad;">dashboard</span></h2>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df_info_prefeitura = load_and_process_ag_info_prefeitura(file_path)
    df_instalacao = load_and_process_ag_instalacao(file_path)
    df_visita = load_and_process_ag_visita(file_path)
    df_servicos = carregar_dados_servicos()
    if not df_servicos.empty:
        df_servicos = atualizar_tempo_servicos(df_servicos)
    df_produtividade, months_prod = load_and_process_produtividade(file_path)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ag Info Prefeitura", "Ag Instalacao", "Ag Visita", "Servicos a Revisar", "Produtividade"])
    
    with tab1:
        st.markdown("### Dashboard de Aguardando Informações da Prefeitura")
        limite_cidades = st.selectbox(
            "Limitar número de cidades no gráfico",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades_info"
        )
        fig_info = generate_ag_info_prefeitura_dashboard(df_info_prefeitura, limite_cidades)
        if fig_info:
            st.plotly_chart(fig_info, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível.")
    
    with tab2:
        st.markdown("### Dashboard de Aguardando Instalação")
        limite_cidades = st.selectbox(
            "Limitar número de cidades no dashboard",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades_instalacao"
        )
        figs_instal, df_relatorio_instal = generate_ag_instalacao_dashboards(df_instalacao, limite_cidades)
        for fig in figs_instal:
            st.plotly_chart(fig, use_container_width=True)
        st.markdown("#### Relatório de Datas por Cidade")
        if not df_relatorio_instal.empty:
            def style_dataframe(df):
                return df.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#4F81BD'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('border', '1px solid #ddd'), ('padding', '8px'), ('text-align', 'center')]},
                    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]},
                    {'selector': 'tr:hover', 'props': [('background-color', '#e0e0e0')]}
                ]).set_properties(**{'font-size': '14px'})
            st.dataframe(style_dataframe(df_relatorio_instal), use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o relatório de datas.")
    
    with tab3:
        st.markdown("### Dashboard de Aguardando Visita Técnica")
        limite_cidades = st.selectbox(
            "Limitar número de cidades no dashboard",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades_visita"
        )
        figs_visita = generate_ag_visita_dashboards(df_visita, limite_cidades)
        for fig in figs_visita:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Dashboard de Serviços a Revisar")
        limite_grafico = st.selectbox(
            "Limitar número de serviços nos gráficos",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_graph_servicos"
        )
        figs_servicos = generate_servicos_a_revisar_dashboards(df_servicos, limite_grafico)
        for fig in figs_servicos:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown("### Dashboard de Produtividade")
        limite_cidades = st.selectbox(
            "Limitar número de cidades no dashboard",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades_produtividade"
        )
        figs_prod = generate_produtividade_dashboard(df_produtividade, months_prod, limite_cidades)
        for fig in figs_prod:
            st.plotly_chart(fig, use_container_width=True)
        if not df_produtividade.empty:
            st.markdown("#### Tabela de Produtividade")
            def style_dataframe(df):
                return df.style.set_table_styles([
                    {'selector': 'th', 'props': [('background-color', '#4F81BD'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center'), ('padding', '8px')]},
                    {'selector': 'td', 'props': [('border', '1px solid #ddd'), ('padding', '8px'), ('text-align', 'center')]},
                    {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]},
                    {'selector': 'tr:hover', 'props': [('background-color', '#e0e0e0')]}
                ]).set_properties(**{'font-size': '14px'})
            st.dataframe(style_dataframe(df_produtividade), use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o dashboard de produtividade.")

if __name__ == "__main__":
    render_dashboard_central()