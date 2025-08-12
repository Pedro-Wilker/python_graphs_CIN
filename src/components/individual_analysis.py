import streamlit as st
import pandas as pd
import plotly.express as px
import calendar
from config.constants import MONTH_TO_NUM, YEAR

def render_individual_tab(df, months):
    """
    Renderiza a aba de Análise Individual.
    """
    cities = df['CIDADE'].sort_values().unique().tolist()
    selected_city = st.selectbox("Selecione uma Cidade", [''] + cities)
    selected_month = st.selectbox("Selecione um Mês para Comparação", [''] + months)

    if selected_city:
        city_df = df[df['CIDADE'] == selected_city]
        
        if city_df.empty:
            st.warning("Nenhum dado encontrado para a cidade selecionada.")
        else:
            st.subheader(f"Análise para a Cidade: {selected_city}")
            
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
            st.plotly_chart(fig_city_bar)
            
            # 3. Gráfico de linhas com produção mês a mês
            fig_city_line = px.line(city_prod, x='Mês', y='Produção', 
                                    title=f'Produção Mensal (Linha) - {selected_city}',
                                    markers=True, text='Produção')
            fig_city_line.update_traces(mode='lines+markers+text', textposition='top center')
            fig_city_line.update_layout(showlegend=True)
            st.plotly_chart(fig_city_line)
            
            # 4. Média de produção diária de cada mês - Gráfico de pizza
            daily_avg = []
            for month in months:
                days_in_month = calendar.monthrange(YEAR, MONTH_TO_NUM[month])[1]
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
                st.plotly_chart(fig_compare_total)
            
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
                st.plotly_chart(fig_compare_month)
            else:
                st.write("Selecione um mês para a comparação por mês.")