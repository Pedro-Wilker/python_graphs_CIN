import streamlit as st
import pandas as pd
import os
from utils.data_utils import load_excel, process_sheet_data
import webbrowser
import time
import re

@st.cache_data
def load_and_process_informacoes(_retry_count=0, _max_retries=2):
    """Carrega e processa a aba Informações com caching e retry."""
    with st.spinner("Carregando dados. Isso pode levar alguns minutos..."):
        try:
            # Verifica se infosgerais.xlsx existe
            infos_file = 'infosgerais.xlsx'
            if os.path.exists(infos_file):
                raw_df = pd.read_excel(infos_file, sheet_name='Informações')
            else:
                # Carrega de load_excel e cria o arquivo se não existir
                raw_df = load_excel('Informações')
                if not raw_df.empty:
                    df = process_sheet_data(raw_df, 'Informações')
                    # Garantir que todas as colunas sejam strings para evitar erros de tipo
                    df = df.astype(str)
                    # Salvar em infosgerais.xlsx
                    df.to_excel(infos_file, sheet_name='Informações', index=False)
                else:
                    st.error("Nenhum dado carregado para a aba 'Informações' no arquivo original.")
                    return pd.DataFrame()

            if raw_df.empty:
                st.error("Nenhum dado carregado para a aba 'Informações' no arquivo infosgerais.xlsx.")
                return pd.DataFrame()

            df = process_sheet_data(raw_df, 'Informações')
            # Forçar conversão para string para evitar erros de serialização
            df = df.astype(str)
            return df
        except Exception as e:
            if _retry_count < _max_retries:
                st.warning(f"Erro ao carregar dados (tentativa {_retry_count + 1}/{_max_retries + 1}): {str(e)}. Tentando novamente...")
                time.sleep(1)  # Pausa de 1 segundo antes de retry
                return load_and_process_informacoes(_retry_count + 1, _max_retries)
            else:
                st.error(f"Falha após {_max_retries + 1} tentativas: {str(e)}")
                return pd.DataFrame()

def generate_whatsapp_link(phone_number):
    if pd.notna(phone_number) and str(phone_number).strip():
        # Remove caracteres não numéricos e adiciona o código do país (ex.: +55 para Brasil)
        phone = re.sub(r'[^\d]', '', str(phone_number))
        if phone and len(phone) >= 10:
            return f"https://wa.me/55{phone}" if phone.startswith('55') else f"https://wa.me/55{phone}"
    return None

def generate_email_link(email, subject="Contato sobre Informações", body="Olá, gostaria de obter mais informações."):
    if pd.notna(email) and str(email).strip():
        return f"mailto:{email}?subject={subject}&body={body}"
    return None

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
    
    # Botão para atualizar informações
    if st.button("Atualizar Infos"):
        st.cache_data.clear()  # Limpa o cache para forçar recarga
        st.experimental_rerun()  # Usa experimental_rerun para melhor controle

    # Carregar dados
    df = load_and_process_informacoes()
    if df.empty:
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `infosgerais.xlsx` ou o arquivo original está no diretório correto.
        - Confirme se a aba 'Informações' existe no arquivo.
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
    
    # Gerar links de WhatsApp
    df['Link WhatsApp'] = df['Telefone Celular chefe de posto'].apply(generate_whatsapp_link)
    df['Link WhatsApp 2'] = df['Telefone do Secretário'].apply(generate_whatsapp_link)
    
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
    
    # Exibir resultados com opções de ação
    if filtered_df.empty and (search_city or search_chief or search_email or search_secretary or search_address or search_pendency):
        st.warning("Nenhum dado encontrado para os critérios de busca.")
    else:
        st.markdown("### Resultados da Busca")
        # Adicionar botões de ação para cada linha
        for index, row in filtered_df.iterrows():
            with st.expander(f"{row['Cidade']} - {row['Nome do chefe de posto']}"):
                st.write(f"**E-mail:** {row['E-mail chefe de posto']}")
                if row['Link WhatsApp']:
                    st.markdown(f"[WhatsApp Chefe]({row['Link WhatsApp']})", unsafe_allow_html=True)
                if row['Link WhatsApp 2']:
                    st.markdown(f"[WhatsApp Secretário]({row['Link WhatsApp 2']})", unsafe_allow_html=True)
                if row['E-mail chefe de posto']:
                    email_link = generate_email_link(row['E-mail chefe de posto'])
                    if st.button("Enviar E-mail", key=f"email_{index}"):
                        webbrowser.open(email_link)
    
    if not (search_city or search_chief or search_email or search_secretary or search_address or search_pendency):
        st.markdown("### Tabela Completa")
        st.dataframe(df, use_container_width=True)