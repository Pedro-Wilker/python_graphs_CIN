import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import numpy as np
import re

@st.cache_data
def load_and_process_produtividade():
    """Carrega e processa a aba Produtividade com caching."""
    try:
        # Caminho do arquivo Excel
        excel_file = "C:/Users/re049227/Documents/pythonGraphs/ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"
        
        # Ler a aba 'Produtividade' diretamente
        raw_df = pd.read_excel(excel_file, sheet_name='Produtividade', engine='openpyxl')
        
        # Normalizar nomes das colunas
        raw_df.columns = raw_df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        raw_df.columns = raw_df.columns.str.replace('PREFEITURA DE', 'PREFEITURAS DE')
        
        # Verificar colunas esperadas
        expected_columns = [
            'CIDADE', 'PERÍODO PREVISTO DE TREINAMENTO', 'REALIZOU TREINAMENTO?', 
            'DATA DA INSTALAÇÃO', 'PREFEITURAS DE', 'DATA DO INÍCIO ATEND.',
            'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO'
        ]
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Produtividade': {', '.join(missing_columns)}")
            # Adiciona colunas ausentes com valores padrão
            for col in missing_columns:
                if col in ['PERÍODO PREVISTO DE TREINAMENTO', 'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'PREFEITURAS DE']:
                    raw_df[col] = ''
                elif col == 'REALIZOU TREINAMENTO?':
                    raw_df[col] = False
                elif col in ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO']:
                    raw_df[col] = 0.0
        
        df = raw_df
        
        # Tratar a coluna PERÍODO PREVISTO DE TREINAMENTO
        if 'PERÍODO PREVISTO DE TREINAMENTO' in df.columns:
            def parse_training_period(period):
                if pd.isna(period) or not isinstance(period, str) or period.strip() == '' or period.strip().upper() == 'N-PREV.':
                    return pd.NaT, pd.NaT
                try:
                    dates = re.split(r'\s*(?:à|a)\s*', period.strip(), flags=re.IGNORECASE)
                    if len(dates) != 2:
                        return pd.NaT, pd.NaT
                    start_date_str, end_date_str = dates
                    start_date_str = start_date_str.strip()
                    if start_date_str.count('/') == 1:
                        start_date = pd.to_datetime(f"{start_date_str}/2025", format='%d/%m/%Y', errors='coerce')
                    else:
                        start_date = pd.to_datetime(start_date_str, format='%d/%m/%Y', errors='coerce')
                    end_date_str = end_date_str.strip()
                    if end_date_str.count('/') == 1:
                        end_date = pd.to_datetime(f"{end_date_str}/2025", format='%d/%m/%Y', errors='coerce')
                    else:
                        end_date = pd.to_datetime(end_date_str, format='%d/%m/%Y', errors='coerce')
                    return start_date, end_date
                except Exception:
                    return pd.NaT, pd.NaT
            
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)
        else:
            df['DATA INÍCIO TREINAMENTO'] = pd.NaT
            df['DATA FIM TREINAMENTO'] = pd.NaT
        
   
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Produtividade: {str(e)}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

def render_produtividade():
    st.markdown("""
        <h3>Produtividade <span class="material-icons" style="vertical-align: middle; color: #004aad;">bar_chart</span></h3>
    """, unsafe_allow_html=True)
    
    df = load_and_process_produtividade()
    
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
    
    # Detectar colunas de meses
    possible_months = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
    months = [m for m in possible_months if m in df.columns]
    
    # Converter colunas de datas para datetime
    date_cols = ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
    
    # Converter colunas de meses para numérico
    for month in months:
        df[month] = pd.to_numeric(df[month], errors='coerce').fillna(0.0)
    
    # Agregar dados por cidade
    agg_dict = {month: 'sum' for month in months}
    agg_dict.update({
        'REALIZOU TREINAMENTO?': 'first',
        'DATA DA INSTALAÇÃO': 'min',
        'DATA DO INÍCIO ATEND.': 'min',
        'DATA INÍCIO TREINAMENTO': 'min',
        'DATA FIM TREINAMENTO': 'min',
        'PREFEITURAS DE': 'first'
    })
    df = df.groupby('CIDADE').agg(agg_dict).reset_index()
    
    # Gráficos gerais
    st.markdown("<h3>Gráficos Gerais</h3>", unsafe_allow_html=True)
    
    # 1. Cidade que mais e menos produziu em cada mês - Gráfico de linhas
    max_min_data = []
    for month in months:
        valid_df = df[df[month] > 0]
        if not valid_df.empty:
            max_city = valid_df.loc[valid_df[month].idxmax(), 'CIDADE'] if valid_df[month].max() > 0 else "Nenhuma"
            max_prod = valid_df[month].max()
            min_city = valid_df.loc[valid_df[month].idxmin(), 'CIDADE'] if valid_df[month].min() >= 0 else "Nenhuma"
            min_prod = valid_df[month].min()
            max_min_data.append({'Mês': month, 'Tipo': 'Máxima', 'Cidade': max_city, 'Produção': max_prod})
            max_min_data.append({'Mês': month, 'Tipo': 'Mínima', 'Cidade': min_city, 'Produção': min_prod})
        else:
            max_min_data.append({'Mês': month, 'Tipo': 'Máxima', 'Cidade': 'Nenhuma', 'Produção': 0})
            max_min_data.append({'Mês': month, 'Tipo': 'Mínima', 'Cidade': 'Nenhuma', 'Produção': 0})
    
    if max_min_data:
        max_min_df = pd.DataFrame(max_min_data)
        fig_max_min = px.line(max_min_df, x='Mês', y='Produção', color='Tipo', 
                              title='Produção Máxima e Mínima por Mês',
                              hover_data=['Cidade'], text='Cidade')
        fig_max_min.update_traces(mode='lines+markers+text', textposition='top center')
        fig_max_min.update_layout(showlegend=True)
        st.plotly_chart(fig_max_min, use_container_width=True)
    else:
        st.warning("Nenhum dado de produção disponível nos meses especificados.")
    
    # 2. Produção geral por mês - Gráfico de colunas
    total_prod = df[months].sum()
    total_prod_df = pd.DataFrame({'Mês': months, 'Produção Total': total_prod})
    fig_total = px.bar(total_prod_df, x='Mês', y='Produção Total', 
                       title='Produção Geral por Mês')
    fig_total.update_traces(texttemplate='%{y}', textposition='outside')
    st.plotly_chart(fig_total, use_container_width=True)
    
    # 3. Total de cidades que realizaram treinamento - Gráfico de pizza
    training_count = df['REALIZOU TREINAMENTO?'].value_counts().reset_index()
    training_count.columns = ['Realizou Treinamento', 'Contagem']
    fig_pizza_training = px.pie(training_count, values='Contagem', names='Realizou Treinamento', 
                                title='Cidades Treinadas vs Não Treinadas')
    fig_pizza_training.update_traces(textinfo='label+percent+value')
    st.plotly_chart(fig_pizza_training, use_container_width=True)
    
    # Criar abas
    tab1, tab2, tab3 = st.tabs(["Análise Individual", "Comparação de Cidades", "Comparação por Datas"])
    
    with tab1:
        cities = df['CIDADE'].sort_values().unique().tolist()
        selected_city = st.selectbox("Selecione uma Cidade", [''] + cities, key="city_individual")
        selected_month = st.selectbox("Selecione um Mês para Comparação", [''] + months, key="month_individual")
        
        if selected_city:
            city_df = df[df['CIDADE'] == selected_city]
            
            if city_df.empty:
                st.warning("Nenhum dado encontrado para a cidade selecionada.")
            else:
                st.markdown(f"<h3>Análise para a Cidade: {selected_city}</h3>", unsafe_allow_html=True)
                
                # 1. Relatório entre período de instalação, treinamento e data de início
                install_date = city_df['DATA DA INSTALAÇÃO'].iloc[0]
                start_date = city_df['DATA DO INÍCIO ATEND.'].iloc[0]
                training_start = city_df['DATA INÍCIO TREINAMENTO'].iloc[0]
                training_end = city_df['DATA FIM TREINAMENTO'].iloc[0]
                if pd.notnull(install_date) and pd.notnull(start_date):
                    diff_days = (start_date - install_date).days
                    st.write(f"Período entre Instalação ({install_date.date()}) e Início de Atendimento ({start_date.date()}): {diff_days} dias")
                else:
                    st.warning("Datas inválidas ou ausentes para a cidade selecionada.")
                if pd.notnull(training_start) and pd.notnull(training_end):
                    st.write(f"Período de Treinamento: {training_start.date()} a {training_end.date()}")
                else:
                    st.write("Período de Treinamento: Dados inválidos ou ausentes.")
                
                # 2. Gráfico de colunas com produção mês a mês
                city_prod = city_df[months].transpose().reset_index()
                city_prod.columns = ['Mês', 'Produção']
                fig_city_bar = px.bar(city_prod, x='Mês', y='Produção', 
                                      title=f'Produção Mês a Mês - {selected_city}')
                fig_city_bar.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_city_bar, use_container_width=True)
                
                # 3. Gráfico de linhas com produção mês a mês
                fig_city_line = px.line(city_prod, x='Mês', y='Produção', 
                                        title=f'Produção Mensal (Linha) - {selected_city}',
                                        markers=True, text='Produção')
                fig_city_line.update_traces(mode='lines+markers+text', textposition='top center')
                fig_city_line.update_layout(showlegend=True)
                st.plotly_chart(fig_city_line, use_container_width=True)
                
                # 4. Média de produção diária de cada mês - Gráfico de pizza
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
                
                # 5. Comparação: Cidade max total, selecionada, min total - Gráfico de linha
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
                
                # 6. Comparação por mês selecionado: Max, selecionada, min no mês - Gráfico de barras
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
                else:
                    st.write("Selecione um mês para a comparação por mês.")
    
    with tab2:
        cities = df['CIDADE'].sort_values().unique().tolist()
        selected_cities = st.multiselect("Selecione Duas ou Mais Cidades para Comparação", cities, key="cities_compare")
        selected_month_comp = st.selectbox("Selecione um Mês para Comparação (Opcional)", [''] + months, key="month_compare")
        
        if len(selected_cities) >= 2:
            compare_df = df[df['CIDADE'].isin(selected_cities)]
            st.markdown(f"<h3>Comparação entre Cidades: {', '.join(selected_cities)}</h3>", unsafe_allow_html=True)
            
            # 1. Relatório entre período de instalação, treinamento e data de início
            period_data = []
            for city in selected_cities:
                city_row = compare_df[compare_df['CIDADE'] == city]
                if not city_row.empty:
                    install_date = city_row['DATA DA INSTALAÇÃO'].iloc[0]
                    start_date = city_row['DATA DO INÍCIO ATEND.'].iloc[0]
                    training_start = city_row['DATA INÍCIO TREINAMENTO'].iloc[0]
                    training_end = city_row['DATA FIM TREINAMENTO'].iloc[0]
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
            
            # Preparar dados para gráficos de produção mês a mês
            compare_prod_df = pd.DataFrame()
            for city in selected_cities:
                city_data = compare_df[compare_df['CIDADE'] == city][months].transpose().reset_index()
                city_data.columns = ['Mês', 'Produção']
                city_data['Cidade'] = city
                compare_prod_df = pd.concat([compare_prod_df, city_data], ignore_index=True)
            
            # 2. Gráfico de colunas com produção mês a mês
            fig_comp_bar = px.bar(compare_prod_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                                  title=f'Produção Mês a Mês - Comparação')
            fig_comp_bar.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig_comp_bar, use_container_width=True)
            
            # 3. Gráfico de linhas com produção mês a mês
            fig_comp_line = px.line(compare_prod_df, x='Mês', y='Produção', color='Cidade',
                                    title=f'Produção Mensal (Linha) - Comparação',
                                    markers=True, text='Produção')
            fig_comp_line.update_traces(mode='lines+markers+text', textposition='top center')
            fig_comp_line.update_layout(showlegend=True)
            st.plotly_chart(fig_comp_line, use_container_width=True)
            
            # 4. Média de produção diária de cada mês - Gráfico de barras
            daily_avg_comp = []
            year = 2025
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
            
            # 5. Comparação por mês selecionado
            if selected_month_comp:
                month_comp_data = compare_df[['CIDADE', selected_month_comp]].copy()
                month_comp_data['Produção'] = month_comp_data[selected_month_comp]
                fig_comp_month = px.bar(month_comp_data, x='CIDADE', y='Produção',
                                        title=f'Comparação no Mês {selected_month_comp}')
                fig_comp_month.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_comp_month, use_container_width=True)
            else:
                st.write("Selecione um mês para a comparação por mês.")
        else:
            st.info("Selecione pelo menos duas cidades para realizar a comparação.")
    
    with tab3:
        st.markdown("<h3>Comparação por Datas</h3>", unsafe_allow_html=True)
        try:
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
            
            month_num = month_to_num.get(selected_month_date)
            if month_num is None:
                st.error(f"Erro: Mês '{selected_month_date}' não encontrado no mapeamento de meses.")
                return
            
            month_num_install = month_to_num.get(selected_month_install) if selected_month_install else None
            
            filtered_df = df.copy()
            if filter_type == "Mesmo Dia e Mês de Data de Instalação":
                if 'DATA DA INSTALAÇÃO' not in df.columns:
                    st.error("Coluna 'DATA DA INSTALAÇÃO' não encontrada no DataFrame.")
                    return
                filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].notna()]
                if selected_day != 'Qualquer':
                    filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].dt.day == int(selected_day)]
                filtered_df = filtered_df[filtered_df['DATA DA INSTALAÇÃO'].dt.month == month_num]
            elif filter_type == "Mesmo Dia e Mês de Data de Início de Atendimento":
                if 'DATA DO INÍCIO ATEND.' not in df.columns:
                    st.error("Coluna 'DATA DO INÍCIO ATEND.' não encontrada no DataFrame.")
                    return
                filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].notna()]
                if selected_day != 'Qualquer':
                    filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].dt.day == int(selected_day)]
                filtered_df = filtered_df[filtered_df['DATA DO INÍCIO ATEND.'].dt.month == month_num]
            else:  # Ambos
                if 'DATA DA INSTALAÇÃO' not in df.columns or 'DATA DO INÍCIO ATEND.' not in df.columns:
                    missing_date_cols = [col for col in ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.'] if col not in df.columns]
                    st.error(f"Colunas de data ausentes no DataFrame: {', '.join(missing_date_cols)}")
                    return
                if month_num_install is None:
                    st.error("Erro: Mês de instalação não especificado para a opção 'Ambos'.")
                    return
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
                    pass
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
            st.error(f"Ocorreu um erro durante a comparação por datas: {str(e)}")
            st.write("Detalhes do erro:")
            st.write(f"- Tipo de comparação: {filter_type}")
            st.write(f"- Dia (Início Atend.): {selected_day}")
            st.write(f"- Mês (Início Atend.): {selected_month_date}")
            if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
                st.write(f"- Dia (Instalação): {selected_day_install}")
                st.write(f"- Mês (Instalação): {selected_month_install}")
            st.write(f"- Limite de cidades: {city_limit}")
            st.write(f"- Colunas no DataFrame: {list(df.columns)}")
            st.write("Verifique se as colunas 'DATA DA INSTALAÇÃO' e 'DATA DO INÍCIO ATEND.' estão no formato 'DD/MM/YYYY' e não contêm valores inválidos.")