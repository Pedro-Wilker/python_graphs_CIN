import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from config.constants import MONTH_TO_NUM, YEAR
import calendar

def render_comparison_cities_tab(df, months):
    """
    Renderiza a aba de Comparação de Cidades.
    """
    cities = df['CIDADE'].sort_values().unique().tolist()
    selected_cities = st.multiselect("Selecione Duas ou Mais Cidades para Comparação", cities)
    selected_month_comp = st.selectbox("Selecione um Mês para Comparação (Opcional)", [''] + months)
    
    if len(selected_cities) >= 2:
        compare_df = df[df['CIDADE'].isin(selected_cities)]
        st.subheader(f"Comparação entre Cidades: {', '.join(selected_cities)}")
        
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
        st.dataframe(period_df)
        
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
        st.plotly_chart(fig_comp_bar)
        
        # 3. Gráfico de linhas com produção mês a mês
        fig_comp_line = px.line(compare_prod_df, x='Mês', y='Produção', color='Cidade',
                                title=f'Produção Mensal (Linha) - Comparação',
                                markers=True, text='Produção')
        fig_comp_line.update_traces(mode='lines+markers+text', textposition='top center')
        fig_comp_line.update_layout(showlegend=True)
        st.plotly_chart(fig_comp_line)
        
        # 4. Média de produção diária de cada mês - Gráfico de barras
        daily_avg_comp = []
        for city in selected_cities:
            city_row = compare_df[compare_df['CIDADE'] == city]
            for month in months:
                days_in_month = calendar.monthrange(YEAR, MONTH_TO_NUM[month])[1]
                prod = city_row[month].sum() if not city_row.empty else 0
                avg = prod / days_in_month if days_in_month > 0 else 0
                daily_avg_comp.append({'Mês': month, 'Média Diária': avg, 'Cidade': city})
        
        daily_avg_comp_df = pd.DataFrame(daily_avg_comp)
        fig_daily_bar = px.bar(daily_avg_comp_df, x='Mês', y='Média Diária', color='Cidade', barmode='group',
                               title=f'Média de Produção Diária por Mês - Comparação')
        fig_daily_bar.update_traces(texttemplate='%{y:.2f}', textposition='outside')
        st.plotly_chart(fig_daily_bar)
        
        # 5. Comparação por mês selecionado
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