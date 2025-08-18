import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

@st.cache_data
def load_and_process_informacoes():
    try:
        raw_df = load_excel('Informações')
        if raw_df.empty:
            st.error("Nenhum dado carregado para a aba 'Informações'. Verifique o arquivo Excel.")
            return pd.DataFrame()
        
        df = process_sheet_data(raw_df, 'Informações')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Informações: {str(e)}")
        return pd.DataFrame()

def render_informacoes():
    st.markdown("""
        <h3>Informações <span class="material-icons" style="vertical-align: middle; color: #004aad;">info</span></h3>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <style>
        .search-container {
            border: 1px solid #004aad;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            background-color: #f0f2f6;
        }
        .search-container h3 {
            color: #004aad;
            margin-bottom: 10px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    df = load_and_process_informacoes()
    if df.empty:
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está no diretório correto.
        - Confirme se a aba 'Informações' existe no arquivo Excel.
        - Assegure-se de que as colunas esperadas estão presentes e formatadas corretamente.
        """)
        return
    
    # Verificar colunas esperadas
    expected_columns = [
        'data/hora', 'Cidade', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
        'Link WhatsApp', 'E-mail chefe de posto', 'Nome do Secretário/Coordenador',
        'Telefone do Secretário', 'Link WhatsApp 2', 'Endereço do Posto', 'CEP',
        'Ponto de referência do endereço', 'Telefone Fixo', 'Horário de abertura',
        'Horário de Fechamento', 'E-mail da Prefeitura', 'Telefone da Prefeitura',
        'PENDÊNCIA P/ VISITA TÉCNICA', 'Código do Posto', 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'
    ]
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Informações': {', '.join(missing_columns)}")
    
    # Carregar dados na sessão
    st.session_state['data_informacoes'] = df
    
    df = st.session_state.get('data_informacoes', df)
    
    # Interface de busca
    with st.container():
        st.markdown('<div class="search-container"><h3>Buscar Informações</h3>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            search_city = st.selectbox("Cidade", [''] + sorted(df['Cidade'].unique().tolist()), key="search_city")
            search_chief = st.text_input("Nome do Chefe de Posto", key="search_chief")
            search_email = st.text_input("E-mail do Chefe de Posto", key="search_email")
        
        with col2:
            search_secretary = st.text_input("Nome do Secretário/Coordenador", key="search_secretary")
            search_address = st.text_input("Endereço do Posto", key="search_address")
            search_pendency = st.text_input("Pendência p/ Visita Técnica", key="search_pendency")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtragem
    filtered_df = df
    if search_city:
        filtered_df = filtered_df[filtered_df['Cidade'].str.contains(search_city, case=False, na=False)]
    if search_chief:
        filtered_df = filtered_df[filtered_df['Nome do chefe de posto'].str.contains(search_chief, case=False, na=False)]
    if search_email:
        filtered_df = filtered_df[filtered_df['E-mail chefe de posto'].str.contains(search_email, case=False, na=False)]
    if search_secretary:
        filtered_df = filtered_df[filtered_df['Nome do Secretário/Coordenador'].str.contains(search_secretary, case=False, na=False)]
    if search_address:
        filtered_df = filtered_df[filtered_df['Endereço do Posto'].str.contains(search_address, case=False, na=False)]
    if search_pendency:
        filtered_df = filtered_df[filtered_df['PENDÊNCIA P/ VISITA TÉCNICA'].str.contains(search_pendency, case=False, na=False)]
    
    # Exibir resultados
    if filtered_df.empty and (search_city or search_chief or search_email or search_secretary or search_address or search_pendency):
        st.warning("Nenhum dado encontrado para os critérios de busca.")
    else:
        st.markdown("### Resultados da Busca")
        st.dataframe(filtered_df, use_container_width=True)
    
    if not (search_city or search_chief or search_email or search_secretary or search_address or search_pendency):
        st.markdown("### Tabela Completa")
        st.dataframe(df, use_container_width=True)