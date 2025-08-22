import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
from utils.data_utils import load_excel, process_sheet_data, SHEET_CONFIG, EXCEL_FILE
from utils.dashboard_utils import (
    generate_ag_info_prefeitura_dashboard,
    generate_ag_instalacao_dashboards,
    generate_ag_visita_dashboards,
    generate_servicos_a_revisar_dashboards,
    generate_produtividade_dashboard
)

@st.cache_data
def load_and_process_ag_info_prefeitura(_file_path=EXCEL_FILE):
    try:
        raw_df = load_excel('Ag_info_prefeitura', _file_path)
        if raw_df.empty:
            return pd.DataFrame()
        expected_columns = list(SHEET_CONFIG['Ag_info_prefeitura']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            for col in missing_columns:
                col_type = SHEET_CONFIG['Ag_info_prefeitura']['columns'][col].get('type', 'string')
                if col_type == 'date':
                    raw_df[col] = pd.NaT
                else:
                    raw_df[col] = ''
        df = process_sheet_data(raw_df, 'Ag_info_prefeitura')
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_and_process_ag_instalacao(_file_path=EXCEL_FILE):
    try:
        raw_df = load_excel('Ag_Instalacao', _file_path)
        if raw_df.empty:
            return pd.DataFrame()
        expected_columns = list(SHEET_CONFIG['Ag_Instalacao']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            for col in missing_columns:
                col_type = SHEET_CONFIG['Ag_Instalacao']['columns'][col].get('type', 'string')
                if col_type == 'date':
                    raw_df[col] = pd.NaT
                elif col_type == 'boolean':
                    raw_df[col] = False
                else:
                    raw_df[col] = ''
        df = process_sheet_data(raw_df, 'Ag_Instalacao')
        return df
    except Exception:
        return pd.DataFrame()

@st.cache_data
def load_and_process_ag_visita(_file_path=EXCEL_FILE):
    try:
        raw_df = load_excel('Ag. Visita', _file_path)
        if raw_df.empty:
            return pd.DataFrame()
        expected_columns = list(SHEET_CONFIG['Ag. Visita']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            for col in missing_columns:
                col_type = SHEET_CONFIG['Ag. Visita']['columns'][col].get('type', 'string')
                if col_type == 'date':
                    raw_df[col] = pd.NaT
                else:
                    raw_df[col] = ''
        df = process_sheet_data(raw_df, 'Ag. Visita')
        return df
    except Exception:
        return pd.DataFrame()

ARQUIVO_SERVICOS = os.path.join(os.path.dirname(__file__), '..', 'revisarservicos.txt')

def parse_data_linha(linha):
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
                meses = {'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 'maio': '05', 'junho': '06',
                         'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'}
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
        return {'SERVIÇO': servico, 'ORGAO': orgao, 'TEMPO': tempo, 'DATA ULTIMA PUBLICACAO': data_formatada}
    except:
        return None

def carregar_dados_servicos():
    try:
        with open(ARQUIVO_SERVICOS, encoding='utf-8') as f:
            linhas = f.readlines()
        dados = [parse_data_linha(linha) for linha in linhas if linha.strip() and parse_data_linha(linha)]
        df = pd.DataFrame(dados)
        return df
    except:
        return pd.DataFrame()

def atualizar_tempo_servicos(df):
    hoje = datetime.now()
    for idx, row in df.iterrows():
        data_str = row['DATA ULTIMA PUBLICACAO']
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
    try:
        raw_df = load_excel('Produtividade', _file_path)
        if raw_df.empty:
            return pd.DataFrame(), []
        raw_df.columns = raw_df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        raw_df.columns = raw_df.columns.str.replace('PREFEITURA DE', 'PREFEITURAS DE')
        expected_columns = list(SHEET_CONFIG['Produtividade']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            for col in missing_columns:
                if col in ['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM', 'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'PREFEITURAS DE']:
                    raw_df[col] = ''
                elif col == 'REALIZOU TREINAMENTO?':
                    raw_df[col] = False
                else:
                    raw_df[col] = 0.0
        df = process_sheet_data(raw_df, 'Produtividade')
        date_cols = ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
        possible_months = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        months = [m for m in possible_months if m in df.columns]
        for month in months:
            df[month] = pd.to_numeric(df[month], errors='coerce').fillna(0.0)
        df['CIDADE'] = df['CIDADE'].astype(str).str.strip().replace('nan', '')
        df['PREFEITURAS DE'] = df['PREFEITURAS DE'].astype(str).str.strip().replace('nan', '')
        df['REALIZOU TREINAMENTO?'] = df['REALIZOU TREINAMENTO?'].apply(lambda x: True if str(x).strip().upper() in ['TRUE', 'SIM', 'X'] else False)
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
    except Exception:
        return pd.DataFrame(), []

def render_dashboard_central(uploaded_file=None):
    st.markdown("""
        <h2>Dashboard Central <span class="material-icons" style="vertical-align: middle; color: #004aad;">dashboard</span></h2>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    
    # Carregar dados
    df_info_prefeitura = load_and_process_ag_info_prefeitura(file_path)
    df_instalacao = load_and_process_ag_instalacao(file_path)
    df_visita = load_and_process_ag_visita(file_path)
    df_servicos = carregar_dados_servicos()
    if not df_servicos.empty:
        df_servicos = atualizar_tempo_servicos(df_servicos)
    df_produtividade, months_prod = load_and_process_produtividade(file_path)
    
    # Abas
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Ag Info Prefeitura", "Ag Instalacao", "Ag Visita", "Servicos a Revisar", "Produtividade"])
    
    with tab1:
        st.markdown("### Dashboard de Aguardando Informações da Prefeitura")
        fig_info = generate_ag_info_prefeitura_dashboard(df_info_prefeitura)
        if fig_info:
            st.plotly_chart(fig_info, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível.")
    
    with tab2:
        st.markdown("### Dashboard de Aguardando Instalação")
        figs_instal, df_relatorio_instal = generate_ag_instalacao_dashboards(df_instalacao)
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
        figs_visita = generate_ag_visita_dashboards(df_visita)
        for fig in figs_visita:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### Dashboard de Serviços a Revisar")
        figs_servicos = generate_servicos_a_revisar_dashboards(df_servicos)
        for fig in figs_servicos:
            st.plotly_chart(fig, use_container_width=True)
    
    with tab5:
        st.markdown("### Dashboard de Produtividade")
        figs_prod = generate_produtividade_dashboard(df_produtividade, months_prod)
        for fig in figs_prod:
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render_dashboard_central()