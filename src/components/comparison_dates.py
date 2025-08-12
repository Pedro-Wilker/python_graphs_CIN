import streamlit as st
import pandas as pd
import plotly.express as px
from config.constants import MONTH_TO_NUM

def render_comparison_dates_tab(df, months):
    """
    Renderiza a aba de Comparação por Datas.
    """
    st.subheader("Comparação por Datas")
    try:
        # Seleção do tipo de comparação
        filter_type = st.selectbox("Selecione o Tipo de Comparação", [
            "Mesmo Dia e Mês de Data de Instalação",
            "Mesmo Dia e Mês de Data de Início de Atendimento",
            "Ambos (Data de Instalação e Início de Atendimento)"
        ])

        # Seleção de dia e mês
        days = ['Qualquer'] + list(range(1, 32))
        months_list = list(MONTH_TO_NUM.keys())
        selected_day = st.selectbox("Selecione o Dia (Início de Atendimento)", days)
        selected_month_date = st.selectbox("Selecione o Mês (Início de Atendimento)", months_list)

        # Seleção de dia e mês para instalação (se necessário)
        selected_day_install = None
        selected_month_install = None
        if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
            selected_day_install = st.selectbox("Selecione o Dia (Instalação)", days)
            selected_month_install = st.selectbox("Selecione o Mês (Instalação)", months_list)

        # Opção para limitar cidades
        limit_cities = st.checkbox("Limitar quantidade de cidades exibidas")
        city_limit = "Sem limite"
        if limit_cities:
            city_limit = st.selectbox("Selecione o número de cidades a exibir", ["2", "5", "10", "Sem limite"])

        # Validação do mês selecionado
        month_num = MONTH_TO_NUM.get(selected_month_date)
        if month_num is None:
            st.error(f"Erro: Mês '{selected_month_date}' não encontrado no mapeamento de meses.")
            return

        month_num_install = MONTH_TO_NUM.get(selected_month_install) if selected_month_install else None

        # Filtrar cidades com base no tipo de comparação
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

        # Aplicar limite de cidades
        if not filtered_df.empty and city_limit != "Sem limite":
            filtered_df['Total Produção'] = filtered_df[months].sum(axis=1)
            filtered_df = filtered_df.sort_values(by='Total Produção', ascending=False)
            try:
                limit = int(city_limit)
                filtered_df = filtered_df.head(limit)
            except ValueError:
                pass  # "Sem limite" já tratado
            filtered_df = filtered_df.drop(columns=['Total Produção'], errors='ignore')

        # Log das cidades filtradas
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

        # Exibir gráficos se houver dados
        if not filtered_df.empty:
            compare_date_df = pd.DataFrame()
            for city in filtered_df['CIDADE']:
                city_data = filtered_df[filtered_df['CIDADE'] == city][months].transpose().reset_index()
                city_data.columns = ['Mês', 'Produção']
                city_data['Cidade'] = city
                compare_date_df = pd.concat([compare_date_df, city_data], ignore_index=True)

            # 1. Gráfico de colunas
            fig_date_bar = px.bar(compare_date_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                                  title=f'Produção Mês a Mês - Comparação por {filter_type}')
            fig_date_bar.update_traces(texttemplate='%{y}', textposition='outside')
            st.plotly_chart(fig_date_bar)

            # 2. Gráfico de linhas
            fig_date_line = px.line(compare_date_df, x='Mês', y='Produção', color='Cidade',
                                    title=f'Produção Mensal (Linha) - Comparação por {filter_type}',
                                    markers=True, text='Produção')
            fig_date_line.update_traces(mode='lines+markers+text', textposition='top center')
            fig_date_line.update_layout(showlegend=True)
            st.plotly_chart(fig_date_line)
        else:
            warning_message = f"Nenhuma cidade encontrada com {filter_type} para "
            warning_message += f"mês {selected_month_date}" if selected_day == 'Qualquer' else f"dia {selected_day}, mês {selected_month_date}"
            if filter_type == "Ambos (Data de Instalação e Início de Atendimento)":
                warning_message += "; Instalação: "
                warning_message += f"mês {selected_month_install}" if selected_day_install == 'Qualquer' else f"dia {selected_day_install}, mês {selected_month_install}"
            st.warning(warning_message)

    except Exception as e:
        st.error(f"Erro na aba Comparação por Datas: {str(e)}")
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