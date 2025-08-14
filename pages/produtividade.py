import streamlit as st
import pandas as pd
import numpy as np
from utils.data_utils import load_excel, process_sheet_data
from utils.plot_utils import (
    plot_max_min_production, plot_total_production, plot_training_pie,
    plot_city_production_bar, plot_city_production_line, plot_daily_avg_pie,
    plot_compare_total, plot_compare_month, plot_compare_cities_bar,
    plot_compare_cities_line, plot_compare_cities_daily_avg, plot_compare_cities_month,
    plot_compare_dates_bar, plot_compare_dates_line
)

def render_produtividade():
    st.subheader("Análise de Produtividade")
    
    try:
        # Carrega e processa os dados da aba 'Produtividade'
        df = load_excel('Produtividade')
        df = process_sheet_data(df, 'Produtividade')
        
        # Verifica colunas esperadas após process_sheet_data
        expected_columns = [
            'CIDADE', 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO', 'PERÍODO PREVISTO DE TREINAMENTO_FIM',
            'REALIZOU TREINAMENTO?', 'DATA DA INSTALAÇÃO', 'PREFEITURA DE', 
            'DATA DO INÍCIO ATEND.', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 
            'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.error(f"Colunas ausentes na aba 'Produtividade': {', '.join(missing_columns)}")
            st.stop()

        # Exibe colunas e tipos de dados para depuração
        st.write("Colunas encontradas na aba 'Produtividade':", df.columns.tolist())
        st.write("Tipos de dados das colunas:", df.dtypes.to_dict())
        
        # Exibe amostra dos dados (primeiras 5 linhas)
        st.write("Amostra dos dados (primeiras 5 linhas):")
        st.dataframe(df.head(5))

        # Abas para organização
        tab0, tab1, tab2, tab3 = st.tabs(["Tabela Completa", "Análise Individual", "Comparação de Cidades", "Comparação por Datas"])

        with tab0:
            st.subheader("Tabela Completa")
            st.dataframe(df)

        with tab1:
            st.subheader("Análise Individual")
            cities = df['CIDADE'].sort_values().unique().tolist()
            selected_city = st.selectbox("Selecione uma Cidade", [''] + cities, key="city_select")
            selected_month = st.selectbox("Selecione um Mês para Comparação", [''] + ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'])

            if selected_city:
                city_df = df[df['CIDADE'] == selected_city]
                if city_df.empty:
                    st.warning("Nenhum dado encontrado para a cidade selecionada.")
                else:
                    st.subheader(f"Análise para a Cidade: {selected_city}")
                    
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

                    fig_bar = plot_city_production_bar(city_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_city)
                    st.plotly_chart(fig_bar)

                    fig_line = plot_city_production_line(city_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_city)
                    st.plotly_chart(fig_line)

                    fig_pie = plot_daily_avg_pie(city_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_city)
                    st.plotly_chart(fig_pie)

                    fig_compare = plot_compare_total(df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_city)
                    if fig_compare:
                        st.plotly_chart(fig_compare)

                    if selected_month:
                        fig_month = plot_compare_month(df, selected_month, selected_city)
                        st.plotly_chart(fig_month)
                    else:
                        st.write("Selecione um mês para a comparação por mês.")

        with tab2:
            st.subheader("Comparação de Cidades")
            cities = df['CIDADE'].sort_values().unique().tolist()
            selected_cities = st.multiselect("Selecione Duas ou Mais Cidades para Comparação", cities)
            selected_month_comp = st.selectbox("Selecione um Mês para Comparação (Opcional)", [''] + ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'])
            
            if len(selected_cities) >= 2:
                compare_df = df[df['CIDADE'].isin(selected_cities)]
                st.subheader(f"Comparação entre Cidades: {', '.join(selected_cities)}")
                
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
                st.dataframe(period_df)
                
                fig_bar = plot_compare_cities_bar(compare_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_cities)
                st.plotly_chart(fig_bar)
                
                fig_line = plot_compare_cities_line(compare_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_cities)
                st.plotly_chart(fig_line)
                
                fig_daily = plot_compare_cities_daily_avg(compare_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], selected_cities)
                st.plotly_chart(fig_daily)
                
                if selected_month_comp:
                    fig_month = plot_compare_cities_month(compare_df, selected_month_comp, selected_cities)
                    st.plotly_chart(fig_month)
                else:
                    st.write("Selecione um mês para a comparação por mês.")
            else:
                st.info("Selecione pelo menos duas cidades para realizar a comparação.")

        with tab3:
            st.subheader("Comparação por Datas")
            month_to_num = {
                'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
                'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
            }

            filter_type = st.selectbox("Selecione o Tipo de Comparação", [
                "Mesmo Dia e Mês de Data de Instalação",
                "Mesmo Dia e Mês de Data de Início de Atendimento",
                "Ambos (Data de Instalação e Início de Atendimento)"
            ])

            days = ['Qualquer'] + list(range(1, 32))
            months_list = list(month_to_num.keys())
            selected_day = st.selectbox("Selecione o Dia (Início de Atendimento)", days)
            selected_month_date = st.selectbox("Selecione o Mês (Início de Atendimento)", months_list)

            selected_day_install = None
            selected_month_install = None
            if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
                selected_day_install = st.selectbox("Selecione o Dia (Instalação)", days)
                selected_month_install = st.selectbox("Selecione o Mês (Instalação)", months_list)

            limit_cities = st.checkbox("Limitar quantidade de cidades exibidas")
            city_limit = "Sem limite"
            if limit_cities:
                city_limit = st.selectbox("Selecione o número de cidades a exibir", ["2", "5", "10", "Sem limite"])

            month_num = month_to_num.get(selected_month_date)
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
                filtered_df['Total Produção'] = filtered_df[['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']].sum(axis=1)
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
            st.write(log_message)

            if not filtered_df.empty:
                fig_bar = plot_compare_dates_bar(filtered_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], filter_type)
                st.plotly_chart(fig_bar)

                fig_line = plot_compare_dates_line(filtered_df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'], filter_type)
                st.plotly_chart(fig_line)
            else:
                warning_message = f"Nenhuma cidade encontrada com {filter_type} para "
                warning_message += f"mês {selected_month_date}" if selected_day == 'Qualquer' else f"dia {selected_day}, mês {selected_month_date}"
                if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
                    warning_message += "; Instalação: "
                    warning_message += f"mês {selected_month_install}" if selected_day_install == 'Qualquer' else f"dia {selected_day_install}, mês {selected_month_install}"
                st.warning(warning_message)

        # Gráficos gerais
        st.subheader("Gráficos Gerais")
        fig_max_min = plot_max_min_production(df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'])
        if fig_max_min:
            st.plotly_chart(fig_max_min)
        else:
            st.warning("Nenhum dado de produção disponível nos meses especificados.")

        fig_total = plot_total_production(df, ['ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO'])
        st.plotly_chart(fig_total)

        fig_pie = plot_training_pie(df)
        st.plotly_chart(fig_pie)

    except Exception as e:
        st.error(f"Erro ao processar a aba Produtividade: {str(e)}")
        st.write("Verifique se a aba 'Produtividade' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()