import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar
import numpy as np

st.title("Análise das Produções de CIN Cidades Bahia")

# Upload do arquivo Excel
uploaded_file = st.file_uploader("Carregue sua planilha Excel (.xlsx)", type="xlsx")

if uploaded_file is not None:
    try:
        # Ler a aba 'Produtividade'
        df = pd.read_excel(uploaded_file, sheet_name='Produtividade')
        
        # Normalizar os nomes das colunas: remover quebras de linha e espaços extras
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Corrigir o nome da coluna PREFEITURA DE para PREFEITURAS DE
        df.columns = df.columns.str.replace('PREFEITURA DE', 'PREFEITURAS DE')
        
        # Normalizar os valores da coluna 'CIDADE'
        if 'CIDADE' in df.columns:
            df['CIDADE'] = df['CIDADE'].astype(str).str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Verificar colunas esperadas
        expected_columns = [
            'CIDADE', 
            'PERÍODO PREVISTO DE TREINAMENTO', 
            'REALIZOU TREINAMENTO?', 
            'DATA DA INSTALAÇÃO', 
            'PREFEITURAS DE', 
            'DATA DO INÍCIO ATEND.', 
            'ABRIL', 
            'MAIO', 
            'JUNHO', 
            'JULHO', 
            'AGOSTO'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Colunas ausentes no Excel: {', '.join(missing_columns)}")
            st.stop()
        
        # Detectar colunas de meses dinamicamente
        possible_months = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        months = [m for m in possible_months if m in df.columns]
        
        # Dicionário para mapear meses para números
        month_to_num = {
            'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
            'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
        }
        
        # Converter colunas de datas para datetime com formato especificado
        date_cols = ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.']
        date_format = '%d/%m/%Y'  # Assumindo formato dia/mês/ano
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
        
        # Converter colunas de meses para numérico
        for month in months:
            df[month] = pd.to_numeric(df[month], errors='coerce').fillna(0)
        
        # Agregar dados por cidade para lidar com possíveis duplicatas
        agg_dict = {month: 'sum' for month in months}
        agg_dict.update({
            'REALIZOU TREINAMENTO?': 'first',
            'DATA DA INSTALAÇÃO': 'min',
            'DATA DO INÍCIO ATEND.': 'min',
            'PERÍODO PREVISTO DE TREINAMENTO': 'first',
            'PREFEITURAS DE': 'first'
        })
        df = df.groupby('CIDADE').agg(agg_dict).reset_index()
        
        # Gráficos gerais (antes de selecionar cidade ou mês)
        st.subheader("Gráficos Gerais")
        
        # 1. Cidade que mais e menos produziu em cada mês - Gráfico de linhas
        max_min_data = []
        for month in months:
            if df[month].sum() > 0:  # Ignorar meses sem dados
                max_city = df.loc[df[month].idxmax(), 'CIDADE']
                max_prod = df[month].max()
                min_city = df.loc[df[month].idxmin(), 'CIDADE']
                min_prod = df[month].min()
                max_min_data.append({'Mês': month, 'Tipo': 'Máxima', 'Cidade': max_city, 'Produção': max_prod})
                max_min_data.append({'Mês': month, 'Tipo': 'Mínima', 'Cidade': min_city, 'Produção': min_prod})
        
        if max_min_data:
            max_min_df = pd.DataFrame(max_min_data)
            fig_max_min = px.line(max_min_df, x='Mês', y='Produção', color='Tipo', 
                                  title='Produção Máxima e Mínima por Mês',
                                  hover_data=['Cidade'])
            fig_max_min.update_traces(mode='lines+markers', text=max_min_df['Produção'], textposition='top center')
            fig_max_min.update_layout(showlegend=True)
            st.plotly_chart(fig_max_min)
        else:
            st.warning("Nenhum dado de produção disponível nos meses especificados.")
        
        # 2. Produção geral por mês - Gráfico de colunas
        total_prod = df[months].sum()
        total_prod_df = pd.DataFrame({'Mês': months, 'Produção Total': total_prod})
        fig_total = px.bar(total_prod_df, x='Mês', y='Produção Total', 
                           title='Produção Geral por Mês')
        fig_total.update_traces(texttemplate='%{y}', textposition='outside')
        st.plotly_chart(fig_total)
        
        # 3. Total de cidades que realizaram treinamento - Gráfico de pizza
        training_count = df['REALIZOU TREINAMENTO?'].value_counts().reset_index()
        training_count.columns = ['Realizou Treinamento', 'Contagem']
        fig_pizza_training = px.pie(training_count, values='Contagem', names='Realizou Treinamento', 
                                    title='Cidades Treinadas vs Não Treinadas')
        fig_pizza_training.update_traces(textinfo='label+percent+value')
        st.plotly_chart(fig_pizza_training)
        
        # Criar abas para análise individual e comparação
        tab1, tab2 = st.tabs(["Análise Individual", "Comparação de Cidades"])
        
        with tab1:
            # Seleção de cidade e mês para análise individual
            cities = df['CIDADE'].unique().tolist()
            selected_city = st.selectbox("Selecione uma Cidade", [''] + cities)
            selected_month = st.selectbox("Selecione um Mês para Comparação", [''] + months)
            
            if selected_city:
                city_df = df[df['CIDADE'] == selected_city]
                
                if city_df.empty:
                    st.warning("Nenhum dado encontrado para a cidade selecionada.")
                else:
                    st.subheader(f"Análise para a Cidade: {selected_city}")
                    
                    # 1. Relatório entre período de instalação e data de início
                    if 'DATA DA INSTALAÇÃO' in city_df.columns and 'DATA DO INÍCIO ATEND.' in city_df.columns:
                        install_date = city_df['DATA DA INSTALAÇÃO'].iloc[0]
                        start_date = city_df['DATA DO INÍCIO ATEND.'].iloc[0]
                        if pd.notnull(install_date) and pd.notnull(start_date):
                            diff_days = (start_date - install_date).days
                            st.write(f"Período entre Instalação ({install_date.date()}) e Início de Atendimento ({start_date.date()}): {diff_days} dias")
                        else:
                            st.warning("Datas inválidas ou ausentes para a cidade selecionada.")
                    
                    # 2. Gráfico de colunas com produção mês a mês
                    city_prod = city_df[months].transpose().reset_index()
                    city_prod.columns = ['Mês', 'Produção']
                    fig_city_bar = px.bar(city_prod, x='Mês', y='Produção', 
                                          title=f'Produção Mês a Mês - {selected_city}')
                    fig_city_bar.update_traces(texttemplate='%{y}', textposition='outside')
                    st.plotly_chart(fig_city_bar)
                    
                    # 3. Gráfico de linhas com produção mês a mês
                    fig_city_line = px.line(city_prod, x='Mês', y='Produção', 
                                            title=f'Produção Mensal (Linha) - {selected_city}',
                                            markers=True)
                    fig_city_line.update_traces(mode='lines+markers', text=city_prod['Produção'], textposition='top center')
                    fig_city_line.update_layout(showlegend=True)
                    st.plotly_chart(fig_city_line)
                    
                    # 4. Média de produção diária de cada mês - Gráfico de pizza
                    daily_avg = []
                    year = 2025  # Ano ajustado
                    for month in months:
                        days_in_month = calendar.monthrange(year, month_to_num[month])[1]
                        prod = city_df[month].iloc[0]
                        avg = prod / days_in_month if days_in_month > 0 else 0
                        daily_avg.append({'Mês': month, 'Média Diária': avg})
                    
                    daily_avg_df = pd.DataFrame(daily_avg)
                    fig_daily_pie = px.pie(daily_avg_df, values='Média Diária', names='Mês', 
                                           title=f'Média de Produção Diária por Mês - {selected_city}')
                    fig_daily_pie.update_traces(textinfo='label+percent+value')
                    st.plotly_chart(fig_daily_pie)
                    
                    # 5. Comparação: Cidade max total, selecionada, min total - Gráfico de linha
                    df['Total Produção'] = df[months].sum(axis=1)
                    max_city_total = df.loc[df['Total Produção'].idxmax(), 'CIDADE']
                    min_city_total = df.loc[df['Total Produção'].idxmin(), 'CIDADE']
                    
                    # Preparar dados para comparação
                    compare_total_df = pd.DataFrame()
                    for city in [max_city_total, selected_city, min_city_total]:
                        city_data = df[df['CIDADE'] == city][months].transpose().reset_index()
                        city_data.columns = ['Mês', 'Produção']
                        city_data['Cidade'] = city
                        compare_total_df = pd.concat([compare_total_df, city_data], ignore_index=True)
                    
                    if not compare_total_df.empty:
                        fig_compare_total = px.line(compare_total_df, x='Mês', y='Produção', color='Cidade',
                                                    title=f'Comparação Produção Total: {max_city_total}, {selected_city}, {min_city_total}',
                                                    markers=True)
                        fig_compare_total.update_traces(mode='lines+markers', text=compare_total_df['Produção'], textposition='top center')
                        fig_compare_total.update_layout(showlegend=True)
                        st.plotly_chart(fig_compare_total)
                    else:
                        st.warning("Não foi possível gerar o gráfico de comparação devido a dados insuficientes.")
                    
                    # 6. Comparação por mês selecionado: Max, selecionada, min no mês - Gráfico de barras
                    if selected_month:
                        month_data = df[['CIDADE', selected_month]].copy()
                        month_data['Produção'] = month_data[selected_month]
                        max_city_month = month_data.loc[month_data['Produção'].idxmax(), 'CIDADE']
                        min_city_month = month_data.loc[month_data['Produção'].idxmin(), 'CIDADE']
                        selected_prod = month_data[month_data['CIDADE'] == selected_city]['Produção'].iloc[0]
                        
                        compare_month_df = pd.DataFrame({
                            'Cidade': [max_city_month, selected_city, min_city_month],
                            'Produção': [month_data['Produção'].max(), selected_prod, month_data['Produção'].min()]
                        })
                        
                        fig_compare_month = px.bar(compare_month_df, x='Cidade', y='Produção',
                                                   title=f'Comparação no Mês {selected_month}: {max_city_month}, {selected_city}, {min_city_month}')
                        fig_compare_month.update_traces(texttemplate='%{y}', textposition='outside')
                        st.plotly_chart(fig_compare_month)
                    else:
                        st.write("Selecione um mês para a comparação por mês.")
        
        with tab2:
            # Seleção de múltiplas cidades e mês para comparação
            cities = df['CIDADE'].unique().tolist()
            selected_cities = st.multiselect("Selecione Duas ou Mais Cidades para Comparação", cities)
            selected_month_comp = st.selectbox("Selecione um Mês para Comparação (Opcional)", [''] + months)
            
            if len(selected_cities) >= 2:
                compare_df = df[df['CIDADE'].isin(selected_cities)]
                
                st.subheader(f"Comparação entre Cidades: {', '.join(selected_cities)}")
                
                # 1. Relatório entre período de instalação e data de início - Mostrar em tabela
                period_data = []
                for city in selected_cities:
                    city_row = compare_df[compare_df['CIDADE'] == city]
                    if not city_row.empty:
                        install_date = city_row['DATA DA INSTALAÇÃO'].iloc[0]
                        start_date = city_row['DATA DO INÍCIO ATEND.'].iloc[0]
                        if pd.notnull(install_date) and pd.notnull(start_date):
                            diff_days = (start_date - install_date).days
                            period_data.append({
                                'Cidade': city, 
                                'Instalação': install_date, 
                                'Início Atend.': start_date, 
                                'Dias': diff_days
                            })
                        else:
                            period_data.append({
                                'Cidade': city, 
                                'Instalação': pd.NaT, 
                                'Início Atend.': pd.NaT, 
                                'Dias': np.nan
                            })
                    else:
                        period_data.append({
                            'Cidade': city, 
                            'Instalação': pd.NaT, 
                            'Início Atend.': pd.NaT, 
                            'Dias': np.nan
                        })
                
                period_df = pd.DataFrame(period_data)
                st.dataframe(period_df)
                
                # Preparar dados para gráficos de produção mês a mês
                compare_prod_df = pd.DataFrame()
                for city in selected_cities:
                    city_data = compare_df[compare_df['CIDADE'] == city][months].transpose().reset_index()
                    city_data.columns = ['Mês', 'Produção']
                    city_data['Cidade'] = city
                    compare_prod_df = pd.concat([compare_prod_df, city_data], ignore_index=True)
                
                # 2. Gráfico de colunas com produção mês a mês (agrupado por cidade)
                fig_comp_bar = px.bar(compare_prod_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                                      title=f'Produção Mês a Mês - Comparação')
                fig_comp_bar.update_traces(texttemplate='%{y}', textposition='outside')
                st.plotly_chart(fig_comp_bar)
                
                # 3. Gráfico de linhas com produção mês a mês
                fig_comp_line = px.line(compare_prod_df, x='Mês', y='Produção', color='Cidade',
                                        title=f'Produção Mensal (Linha) - Comparação',
                                        markers=True)
                fig_comp_line.update_traces(mode='lines+markers', text=compare_prod_df['Produção'], textposition='top center')
                fig_comp_line.update_layout(showlegend=True)
                st.plotly_chart(fig_comp_line)
                
                # 4. Média de produção diária de cada mês - Gráfico de barras
                daily_avg_comp = []
                year = 2025  # Ano ajustado
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
                st.plotly_chart(fig_daily_bar)
                
                # 5. Comparação por mês selecionado: Barras para o mês específico
                if selected_month_comp:
                    month_comp_data = compare_df[['CIDADE', selected_month_comp]].copy()
                    month_comp_data['Produção'] = month_comp_data[selected_month_comp]
                    fig_comp_month = px.bar(month_comp_data, x='CIDADE', y='Produção',
                                            title=f'Comparação no Mês {selected_month_comp}')
                    fig_comp_month.update_traces(texttemplate='%{y}', textposition='outside')
                    st.plotly_chart(fig_comp_month)
                else:
                    st.write("Selecione um mês para a comparação por mês.")
            else:
                st.info("Selecione pelo menos duas cidades para realizar a comparação.")
    
    except Exception as e:
        st.error(f"Erro ao carregar o Excel: {str(e)}")
        st.write("Verifique se o arquivo tem a aba 'Produtividade' e as colunas esperadas.")