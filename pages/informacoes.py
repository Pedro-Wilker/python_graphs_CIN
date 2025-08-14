import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_date_columns

def render_informacoes():
    st.subheader("Informações")
    
    try:
        # Carrega a aba 'Informações'
        df = load_excel('Informações')
        
        # Colunas esperadas
        expected_columns = [
            'data/hora', 'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
            'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
            'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
            'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
            'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura'
        ]
        # Verifica colunas ausentes
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Informações': {', '.join(missing_columns)}")
        
        # Exibe os nomes das colunas encontradas para depuração
        st.write("Colunas encontradas na aba 'Informações':", df.columns.tolist())
        
        # Exibe os tipos de dados de cada coluna
        st.write("Tipos de dados das colunas:", df.dtypes.to_dict())

        # Exibe uma amostra dos dados da coluna 'E-mail chefe de posto' para depuração
        if 'E-mail chefe de posto' in df.columns:
            st.write("Amostra dos dados na coluna 'E-mail chefe de posto' (primeiras 10 linhas):")
            st.write(df['E-mail chefe de posto'].head(10).tolist())
        else:
            st.error("Coluna 'E-mail chefe de posto' não encontrada no DataFrame.")

        # Converte colunas de texto para string, tratando valores nulos e não-textuais
        string_columns = [
            'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
            'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
            'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
            'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
            'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura'
        ]
        for col in string_columns:
            if col in df.columns:
                # Converte tudo para string, tratando NaN, números e outros tipos
                df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '').replace('nan', '')

        # Converte a coluna de data/hora
        if 'data/hora' in df.columns:
            df['data/hora'] = pd.to_datetime(df['data/hora'], format='%d/%m/%Y %H:%M', errors='coerce')
        else:
            st.warning("Coluna 'data/hora' não encontrada na aba 'Informações'.")

        # Filtro por cidade
        cities = df['Cidade'].sort_values().unique().tolist()
        selected_city = st.selectbox("Selecione uma Cidade", [''] + cities)

        if selected_city:
            filtered_df = df[df['Cidade'] == selected_city]
            if filtered_df.empty:
                st.warning("Nenhum dado encontrado para a cidade selecionada.")
            else:
                st.dataframe(filtered_df)
        else:
            st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Informações: {str(e)}")
        st.write("Verifique se a aba 'Informações' existe no arquivo Excel e contém as colunas esperadas.")
        st.write("Certifique-se de que a coluna 'E-mail chefe de posto' contém apenas textos (e-mails válidos, 'N/A' ou vazio) e não números ou outros tipos de dados.")
        st.stop()