import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_date_columns

def render_informacoes():
    st.subheader("Informações")
    
    try:
        df = load_excel('Informações')
        
        expected_columns = [
            'data/hora', 'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
            'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
            'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
            'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
            'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Informações': {', '.join(missing_columns)}")

        if 'data/hora' in df.columns:
            df['data/hora'] = pd.to_datetime(df['data/hora'], format='%d/%m/%Y %H:%M', errors='coerce')

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
        st.stop()