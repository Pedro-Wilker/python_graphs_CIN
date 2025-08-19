import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import numpy as np
import re
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_produtividade(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Produtividade com caching."""
    try:
        raw_df = load_excel('Produtividade', _file_path)
        
        # Normalizar nomes das colunas
        raw_df.columns = raw_df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        raw_df.columns = raw_df.columns.str.replace('PREFEITURA DE', 'PREFEITURAS DE')
        
        # Verificar colunas esperadas
        expected_columns = list(SHEET_CONFIG['Produtividade']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Produtividade': {', '.join(missing_columns)}")
            for col in missing_columns:
                if col in ['PERÍODO PREVISTO DE TREINAMENTO', 'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'PREFEITURAS DE']:
                    raw_df[col] = ''
                elif col == 'REALIZOU TREINAMENTO?':
                    raw_df[col] = False
                elif col in ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']:
                    raw_df[col] = 0.0
        
        df = process_sheet_data(raw_df, 'Produtividade')
        
        # Converter colunas de meses para numérico
        possible_months = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        months = [m for m in possible_months if m in df.columns]
        for month in months:
            df[month] = pd.to_numeric(df[month], errors='coerce').fillna(0.0)
        
        return df, months
    except Exception as e:
        st.error(f"Erro ao processar a aba Produtividade: {str(e)}")
        return pd.DataFrame(), []

def render_produtividade(uploaded_file=None):
    st.markdown("""
        <h3>Produtividade <span class="material-icons" style="vertical-align: middle; color: #004aad;">bar_chart</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df, months = load_and_process_produtividade(file_path)
    
    if df.empty:
        st.error("Nenhum dado disponível para a aba Produtividade. Verifique o arquivo Excel.")
        return
    
    # Filtrar linhas válidas
    df['CIDADE'] = df['CIDADE'].astype(str).str.strip().replace('nan', '')
    df['PREFEITURAS DE'] = df['PREFEITURAS DE'].astype(str).str.strip().replace('nan', '')
    df['REALIZOU TREINAMENTO?'] = df['REALIZOU TREINAMENTO?'].apply(lambda x: True if str(x).strip().upper() in ['TRUE', 'SIM', 'X'] else False)
    df = df[df['CIDADE'].notna() & (df['CIDADE'] != '') & (df['CIDADE'] != 'TOTAL')]
    df = df[df['PREFEITURAS DE'].notna() & (df['PREFEITURAS DE'] != '')]
    
    duplicate_cities = df[df['CIDADE'].duplicated(keep=False)]['CIDADE'].unique()
    if len(duplicate_cities) > 0:
        st.warning(f"Cidades duplicadas encontradas: {duplicate_cities.tolist()}. Agregando dados por cidade.")
    
    # Converter colunas de datas
    date_cols = ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
    
    # Agregar dados por cidade
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
    
    # Aba de navegação
    tab1, tab2, tab3, tab4 = st.tabs(["Dados", "Análise Individual", "Comparação de Cidades", "Comparação por Datas"])
    
    with tab1:
        st.markdown("### Tabela Completa")
        st.dataframe(df, use_container_width=True)
        
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            periodo_inicio = st.date_input("Período Previsto de Treinamento - Início (opcional)", value=None, key="new_periodo_inicio")
            periodo_fim = st.date_input("Período Previsto de Treinamento - Fim (opcional)", value=None, key="new_periodo_fim")
            realizou_treinamento = st.checkbox("Realizou Treinamento?", key="new_realizou_treinamento")
            data_instalacao = st.date_input("Data da Instalação (opcional)", value=None, key="new_data_instalacao")
            prefeitura = st.text_input("Prefeituras de", key="new_prefeitura")
            data_inicio_atend = st.date_input("Data do Início Atend. (opcional)", value=None, key="new_data_inicio_atend")
            month_inputs = {month: st.number_input(f"{month}", min_value=0.0, step=1.0, key=f"new_{month.lower()}") for month in months}
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade and prefeitura:
                    novo = {
                        'CIDADE': cidade,
                        'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO': periodo_inicio.strftime('%d/%m/%Y') if periodo_inicio else '',
                        'PERÍODO PREVISTO DE TREINAMENTO_FIM': periodo_fim.strftime('%d/%m/%Y') if periodo_fim else '',
                        'REALIZOU TREINAMENTO?': realizou_treinamento,
                        'DATA DA INSTALAÇÃO': data_instalacao.strftime('%d/%m/%Y') if data_instalacao else '',
                        'PREFEITURAS DE': prefeitura,
                        'DATA DO INÍCIO ATEND.': data_inicio_atend.strftime('%d/%m/%Y') if data_inicio_atend else ''
                    }
                    for month in months:
                        novo[month] = month_inputs[month]
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Produtividade', file_path):
                        st.cache_data.clear()
                        st.success("Registro adicionado!")
                        st.rerun()
                else:
                    st.error("Cidade e Prefeituras de são obrigatórios.")
        
        # Editar ou Apagar Registro
        with st.expander("Editar ou Apagar Registro"):
            if not df.empty:
                idx = st.selectbox("Selecione uma linha", df.index, key="edit_idx")
                row = df.loc[idx]
                
                with st.expander("Editar Registro"):
                    cidade_edit = st.text_input("Cidade", value=row['CIDADE'], key="edit_cidade")
                    periodo_inicio_edit = st.date_input("Período Previsto de Treinamento - Início (opcional)", 
                                                        value=pd.to_datetime(row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO']) and row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'] else None,
                                                        key="edit_periodo_inicio")
                    periodo_fim_edit = st.date_input("Período Previsto de Treinamento - Fim (opcional)", 
                                                     value=pd.to_datetime(row['PERÍODO PREVISTO DE TREINAMENTO_FIM'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['PERÍODO PREVISTO DE TREINAMENTO_FIM']) and row['PERÍODO PREVISTO DE TREINAMENTO_FIM'] else None,
                                                     key="edit_periodo_fim")
                    realizou_treinamento_edit = st.checkbox("Realizou Treinamento?", value=row['REALIZOU TREINAMENTO?'], key="edit_realizou_treinamento")
                    data_instalacao_edit = st.date_input("Data da Instalação (opcional)", 
                                                        value=pd.to_datetime(row['DATA DA INSTALAÇÃO'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA INSTALAÇÃO']) and row['DATA DA INSTALAÇÃO'] else None,
                                                        key="edit_data_instalacao")
                    prefeitura_edit = st.text_input("Prefeituras de", value=row['PREFEITURAS DE'], key="edit_prefeitura")
                    data_inicio_atend_edit = st.date_input("Data do Início Atend. (opcional)", 
                                                          value=pd.to_datetime(row['DATA DO INÍCIO ATEND.'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DO INÍCIO ATEND.']) and row['DATA DO INÍCIO ATEND.'] else None,
                                                          key="edit_data_inicio_atend")
                    month_inputs_edit = {month: st.number_input(f"{month}", min_value=0.0, step=1.0, value=float(row[month]) if pd.notna(row[month]) else 0.0, key=f"edit_{month.lower()}") for month in months}
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit and prefeitura_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'] = periodo_inicio_edit.strftime('%d/%m/%Y') if periodo_inicio_edit else ''
                            df.at[idx, 'PERÍODO PREVISTO DE TREINAMENTO_FIM'] = periodo_fim_edit.strftime('%d/%m/%Y') if periodo_fim_edit else ''
                            df.at[idx, 'REALIZOU TREINAMENTO?'] = realizou_treinamento_edit
                            df.at[idx, 'DATA DA INSTALAÇÃO'] = data_instalacao_edit.strftime('%d/%m/%Y') if data_instalacao_edit else ''
                            df.at[idx, 'PREFEITURAS DE'] = prefeitura_edit
                            df.at[idx, 'DATA DO INÍCIO ATEND.'] = data_inicio_atend_edit.strftime('%d/%m/%Y') if data_inicio_atend_edit else ''
                            for month in months:
                                df.at[idx, month] = month_inputs_edit[month]
                            if save_excel(df, 'Produtividade', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade e Prefeituras de são obrigatórios.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Produtividade', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")
    
    with tab2:
        # [Existing Análise Individual code, unchanged]
        cities = df['CIDADE'].sort_values().unique().tolist()
        selected_city = st.selectbox("Selecione uma Cidade", [''] + cities, key="city_individual")
        selected_month = st.selectbox("Selecione um Mês para Comparação", [''] + months, key="month_individual")
        
        if selected_city:
            city_df = df[df['CIDADE'] == selected_city]
            
            if city_df.empty:
                st.warning("Nenhum dado encontrado para a cidade selecionada.")
            else:
                st.markdown(f"<h3>Análise para a Cidade: {selected_city}</h3>", unsafe_allow_html=True)
                
                install_date = city_df['DATA DA INSTALAÇÃO'].iloc[0]
                start_date = city_df['DATA DO INÍCIO ATEND.'].iloc[0]
                training_start = city_df['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'].iloc[0]
                training_end = city_df['PERÍODO PREVISTO DE TREINAMENTO_FIM'].iloc[0]
                if pd.notnull(install_date) and pd.notnull(start_date):
                    diff_days = (start_date - install_date).days
                    st.write(f"Período entre Instalação ({install_date.date()}) e Início de Atendimento ({start_date.date()}): {diff_days} dias")
                else:
                    st.warning("Datas inválidas ou ausentes para a cidade selecionada.")
                if pd.notnull(training_start) and pd.notnull(training_end):
                    st.write(f"Período de Treinamento: {training_start.date()} a {training_end.date()}")
                else:
                    st.write("Período de Treinamento: Dados inválidos ou ausentes.")
                
                city_prod = city_df[months].transpose().reset_index()
                city_prod.columns = ['Mês', 'Produção']
                fig_city_bar = px.bar(city_prod, x='Mês', y='Produção', 
                                      title=f'Produção Mês a Mês - {selected_city}')
                fig_city_bar.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_city_bar, use_container_width=True)
                
                fig_city_line = px.line(city_prod, x='Mês', y='Produção', 
                                        title=f'Produção Mensal (Linha) - {selected_city}',
                                        markers=True, text='Produção')
                fig_city_line.update_traces(mode='lines+markers+text', textposition='top center')
                fig_city_line.update_layout(showlegend=True)
                st.plotly_chart(fig_city_line, use_container_width=True)
                
                daily_avg = []
                year = 2025
                month_to_num = {
                    'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
                    'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
                }
                for month in months:
                    days_in_month = calendar.monthrange(year, month_to_num[month])[1]
                    prod = city_df[month].iloc[0]
                    avg = prod / days_in_month if days_in_month > 0 else 0
                    daily_avg.append({'Mês': month, 'Média Diária': avg})
                
                daily_avg_df = pd.DataFrame(daily_avg)
                fig_daily_pie = px.pie(daily_avg_df, values='Média Diária', names='Mês', 
                                       title=f'Média de Produção Diária por Mês - {selected_city}')
                fig_daily_pie.update_traces(textinfo='label+percent+value')
                st.plotly_chart(fig_daily_pie, use_container_width=True)
                
                df['Total Produção'] = df[months].sum(axis=1)
                valid_total_df = df[df['Total Produção'] > 0]
                max_city_total = valid_total_df.loc[valid_total_df['Total Produção'].idxmax(), 'CIDADE'] if not valid_total_df.empty else "Nenhuma"
                min_city_total = valid_total_df.loc[valid_total_df['Total Produção'].idxmin(), 'CIDADE'] if not valid_total_df.empty else "Nenhuma"
                
                compare_total_df = pd.DataFrame()
                for city in [max_city_total, selected_city, min_city_total]:
                    city_data = df[df['CIDADE'] == city][months].transpose().reset_index()
                    city_data.columns = ['Mês', 'Produção']
                    city_data['Cidade'] = city
                    compare_total_df = pd.concat([compare_total_df, city_data], ignore_index=True)
                
                if not compare_total_df.empty:
                    fig_compare_total = px.line(compare_total_df, x='Mês', y='Produção', color='Cidade',
                                                title=f'Comparação Produção Total: {max_city_total}, {selected_city}, {min_city_total}',
                                                markers=True, text='Produção')
                    fig_compare_total.update_traces(mode='lines+markers+text', textposition='top center')
                    fig_compare_total.update_layout(showlegend=True)
                    st.plotly_chart(fig_compare_total, use_container_width=True)
                
                if selected_month:
                    month_data = df[['CIDADE', selected_month]].copy()
                    month_data['Produção'] = month_data[selected_month]
                    valid_month_data = month_data[month_data['Produção'] > 0]
                    max_city_month = valid_month_data.loc[valid_month_data['Produção'].idxmax(), 'CIDADE'] if not valid_month_data.empty else "Nenhuma"
                    min_city_month = valid_month_data.loc[valid_month_data['Produção'].idxmin(), 'CIDADE'] if not valid_month_data.empty else "Nenhuma"
                    selected_prod = month_data[month_data['CIDADE'] == selected_city]['Produção'].iloc[0] if not month_data[month_data['CIDADE'] == selected_city].empty else 0
                    
                    compare_month_df = pd.DataFrame({
                        'Cidade': [max_city_month, selected_city, min_city_month],
                        'Produção': [
                            valid_month_data['Produção'].max() if not valid_month_data.empty else 0,
                            selected_prod,
                            valid_month_data['Produção'].min() if not valid_month_data.empty else 0
                        ]
                    })
                    fig_compare_month = px.bar(compare_month_df, x='Cidade', y='Produção',
                                               title=f'Comparação no Mês {selected_month}: {max_city_month}, {selected_city}, {min_city_month}')
                    fig_compare_month.update_traces(texttemplate='%{y}', textposition='outside')
                    st.plotly_chart(fig_compare_month, use_container_width=True)
    
    with tab3:
        # [Existing Comparação de Cidades code, unchanged]
        cities = df['CIDADE'].sort_values().unique().tolist()
        selected_cities = st.multiselect("Selecione Duas ou Mais Cidades para Comparação", cities, key="cities_compare")
        selected_month_comp = st.selectbox("Selecione um Mês para Comparação (Opcional)", [''] + months, key="month_compare")
        
        if len(selected_cities) >= 2:
            compare_df = df[df['CIDADE'].isin(selected_cities)]
            st.markdown(f"<h3>Comparação entre Cidades: {', '.join(selected_cities)}</h3>", unsafe_allow_html=True)
            
            period_data = []
            for city in selected_cities:
                city_row = compare_df[compare_df['CIDADE'] == city]
                if not city_row.empty:
                    install_date = city_row['DATA DA INSTALAÇÃO'].iloc[0]
                    start_date = city_row['DATA DO INÍCIO ATEND.'].iloc[0]
                    training_start = city_row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'].iloc[0]
                    training_end = city_row['PERÍODO PREVISTO DE TREINAMENTO_FIM'].iloc[0]
                    diff_days = (start_date - install_date).days if pd.notnull(install_date) and pd.notnull(start_date) else np.nan
                    period_data.append({
                        'Cidade': city, 
                        'Instalação': install_date, 
                        'Início Atend.': start_date, 
                        'Início Treinamento': training_start,
                        'Fim Treinamento': training_end,
                        'Dias (Instalação-Atend.)': diff_days
                    })
                else:
                    period_data.append({
                        'Cidade': city, 
                        'Instalação': pd.NaT, 
                        'Início Atend.': pd.NaT, 
                        'Início Treinamento': pd.NaT,
                        'Fim Treinamento': pd.NaT,
                        'Dias (Instalação-Atend.)': np.nan
                    })
            
            period_df = pd.DataFrame(period_data)
            st.dataframe(period_df, use_container_width=True)
            
            compare_prod_df = pd.DataFrame()
            for city in selected_cities:
                city_data = compare_df[compare_df['CIDADE'] == city][months].transpose().reset_index()
                city_data.columns = ['Mês', 'Produção']
                city_data['Cidade'] = city
                compare_prod_df = pd.concat([compare_prod_df, city_data], ignore_index=True)
            
            fig_comp_bar = px.bar(compare_prod_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                                  title=f'Produção Mês a Mês - Comparação')
            fig_comp_bar.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig_comp_bar, use_container_width=True)
            
            fig_comp_line = px.line(compare_prod_df, x='Mês', y='Produção', color='Cidade',
                                    title=f'Produção Mensal (Linha) - Comparação',
                                    markers=True, text='Produção')
            fig_comp_line.update_traces(mode='lines+markers+text', textposition='top center')
            fig_comp_line.update_layout(showlegend=True)
            st.plotly_chart(fig_comp_line, use_container_width=True)
            
            daily_avg_comp = []
            year = 2025
            month_to_num = {
                'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
                'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
            }
            for city in selected_cities:
                city_row = compare_df[compare_df['CIDADE'] == city]
                for month in months:
                    days_in_month = calendar.monthrange(year, month_to_num[month])[1]
                    prod = city_row[month].sum() if not city_row.empty else 0
                    avg = prod / days_in_month if days_in_month > 0 else 0
                    daily_avg_comp.append({'Mês': month, 'Média Diária': avg, 'Cidade': city})
            
            daily_avg_comp_df = pd.DataFrame(daily_avg_comp)
            fig_daily_bar = px.bar(daily_avg_comp_df, x='Mês', y='Média Diária', color='Cidade', barmode='group',
                                   title=f'Média de Produção Diária por Mês - Comparação')
            fig_daily_bar.update_traces(texttemplate='%{y:.2f}', textposition='outside')
            st.plotly_chart(fig_daily_bar, use_container_width=True)
            
            if selected_month_comp:
                month_comp_data = compare_df[['CIDADE', selected_month_comp]].copy()
                month_comp_data['Produção'] = month_comp_data[selected_month_comp]
                fig_comp_month = px.bar(month_comp_data, x='CIDADE', y='Produção',
                                        title=f'Comparação no Mês {selected_month_comp}')
                fig_comp_month.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_comp_month, use_container_width=True)
    
    with tab4:
        # [Corrected Comparação por Datas code]
        st.markdown("<h3>Comparação por Datas</h3>", unsafe_allow_html=True)
        month_to_num = {
            'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
            'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
        }
        
        filter_type = st.selectbox("Selecione o Tipo de Comparação", [
            "Mesmo Dia e Mês de Data de Instalação",
            "Mesmo Dia e Mês de Data de Início de Atendimento",
            "Ambos (Data de Instalação e Início de Atendimento)"
        ], key="filter_type")
        
        days = ['Qualquer'] + list(range(1, 32))
        months_list = list(month_to_num.keys())
        selected_day = st.selectbox("Selecione o Dia (Início de Atendimento)", days, key="day_attend")
        selected_month_date = st.selectbox("Selecione o Mês (Início de Atendimento)", months_list, key="month_attend")
        
        selected_day_install = None
        selected_month_install = None
        if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
            selected_day_install = st.selectbox("Selecione o Dia (Instalação)", days, key="day_install")
            selected_month_install = st.selectbox("Selecione o Mês (Instalação)", months_list, key="month_install")
        
        limit_cities = st.checkbox("Limitar quantidade de cidades exibidas", key="limit_cities")
        city_limit = "Sem limite"
        if limit_cities:
            city_limit = st.selectbox("Selecione o número de cidades a exibir", ["2", "5", "10", "Sem limite"], key="city_limit")
        
        try:
            month_num = month_to_num.get(selected_month_date)
            if month_num is None:
                st.error(f"Erro: Mês '{selected_month_date}' não encontrado no mapeamento de meses.")
                return
            
            month_num_install = month_to_num.get(selected_month_install) if selected_month_install else None
            
            filtered_df = df.copy()
            if filter_type == "Mesmo Dia e Mês de Data de Instalação":
                filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].notna()]
                if selected_day != 'Qualquer':
                    filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].dt.day == int(selected_day)]
                filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].dt.month == month_num]
            elif filter_type == "Mesmo Dia e Mês de Data de Início de Atendimento":
                filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].notna()]
                if selected_day != 'Qualquer':
                    filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].dt.day == int(selected_day)]
                filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].dt.month == month_num]
            else:
                filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].notna() & filtered_df['DATA DO INÍCIO ATEND.'].notna()]
                if selected_day_install != 'Qualquer':
                    filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].dt.day == int(selected_day_install)]
                filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].dt.month == month_num_install]
                if selected_day != 'Qualquer':
                    filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].dt.day == int(selected_day)]
                filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].dt.month == month_num]
            
            if not filtered_df.empty and city_limit != "Sem limite":
                filtered_df['Total Produção'] = filtered_df[months].sum(axis=1)
                filtered_df = filtered_df.sort_values(by='Total Produção', ascending=False)
                try:
                    limit = int(city_limit)
                    filtered_df = filtered_df.head(limit)
                except ValueError:
                    st.error("Erro: Limite de cidades inválido.")
                    return
                filtered_df = filtered_df.drop(columns=['Total Produção'], errors='ignore')
            
            log_message = f"Cidades filtradas para {filter_type} (Início Atend.: "
            log_message += f"Mês {selected_month_date}" if selected_day == 'Qualquer' else f"Dia {selected_day}, Mês {selected_month_date}"
            if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
                log_message += f"; Instalação: "
                log_message += f"Mês {selected_month_install}" if selected_day_install == 'Qualquer' else f"Dia {selected_day_install}, Mês {selected_month_install}"
            log_message += f") - Exibindo {len(filtered_df)} cidade(s)"
            if limit_cities and city_limit != "Sem limite":
                log_message += f" (limitado a {city_limit})"
            log_message += ": " + str(filtered_df['CIDADE'].tolist())
            st.write(log_message)
            
            if not filtered_df.empty:
                compare_date_df = pd.DataFrame()
                for city in filtered_df['CIDADE']:
                    city_data = filtered_df[filtered_df['CIDADE'] == city][months].transpose().reset_index()
                    city_data.columns = ['Mês', 'Produção']
                    city_data['Cidade'] = city
                    compare_date_df = pd.concat([compare_date_df, city_data], ignore_index=True)
                
                fig_date_bar = px.bar(compare_date_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                                      title=f'Produção Mês a Mês - Comparação por {filter_type}')
                fig_date_bar.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_date_bar, use_container_width=True)
                
                fig_date_line = px.line(compare_date_df, x='Mês', y='Produção', color='Cidade',
                                        title=f'Produção Mensal (Linha) - Comparação por {filter_type}',
                                        markers=True, text='Produção')
                fig_date_line.update_traces(mode='lines+markers+text', textposition='top center')
                fig_date_line.update_layout(showlegend=True)
                st.plotly_chart(fig_date_line, use_container_width=True)
            else:
                warning_message = f"Nenhuma cidade encontrada com {filter_type} para "
                warning_message += f"mês {selected_month_date}" if selected_day == 'Qualquer' else f"dia {selected_day}, mês {selected_month_date}"
                if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
                    warning_message += "; Instalação: "
                    warning_message += f"mês {selected_month_install}" if selected_day_install == 'Qualquer' else f"dia {selected_day_install}, mês {selected_month_install}"
                st.warning(warning_message)
        except Exception as e:
            st.error(f"Erro ao processar a comparação por datas: {str(e)}")
            return