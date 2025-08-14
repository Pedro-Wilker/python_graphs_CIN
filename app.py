import streamlit as st
from pages.produtividade import render_produtividade
from pages.geral_amplo import render_geral_amplo
from pages.lista_x import render_lista_x
from pages.geral_resumo import render_geral_resumo
from pages.visitas_realizadas import render_visitas_realizadas
from pages.ag_visita import render_ag_visita
from pages.ag_info_prefeitura import render_ag_info_prefeitura
from pages.publicados import render_publicados
from pages.ag_instalacao import render_ag_instalacao
from pages.instalados import render_instalados
from pages.funcionando import render_funcionando
from pages.treina_turma import render_treina_turma
from pages.treina_cidade import render_treina_cidade
from pages.informacoes import render_informacoes
from pages.chefes_posto import render_chefes_posto
from pages.upload_excel import render_upload_excel

# Configuração inicial da página
st.set_page_config(page_title="Manipulador Excel - SAEB - SAV - DOS", layout="wide")

# Estilo CSS para botões quadrados com bordas arredondadas e animação de hover
st.markdown("""
    <style>
    .button-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    .custom-button {
        width: 200px;
        height: 200px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 15px;
        border: 2px solid #004aad;
        background-color: #f0f2f6;
        color: #004aad;
        font-size: 18px;
        font-weight: bold;
        text-align: center;
        transition: all 0.3s ease;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        cursor: pointer;
    }
    .custom-button:hover {
        background-color: #004aad;
        color: white;
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .custom-button img {
        width: 50px;
        height: 50px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o estado da sessão para controle de navegação
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

# Função para atualizar a página atual
def set_page(page):
    st.session_state['current_page'] = page

# Sidebar com navegação
st.sidebar.title("Navegação")
aba = st.sidebar.selectbox(
    "Selecione a Aba",
    [
        "Home", "Produtividade", "Geral Amplo", "Lista X", "Geral Resumo",
        "Visitas Realizadas", "Ag. Visita", "Ag. Info Prefeitura",
        "Publicados", "Ag. Instalação", "Instalados", "Funcionando",
        "Treina Turma", "Treina Cidade", "Informações", "Chefes Posto",
        "Upload Excel"
    ],
    index=['Home', 'Produtividade', 'Geral Amplo', 'Lista X', 'Geral Resumo',
           'Visitas Realizadas', 'Ag. Visita', 'Ag. Info Prefeitura',
           'Publicados', 'Ag. Instalação', 'Instalados', 'Funcionando',
           'Treina Turma', 'Treina Cidade', 'Informações', 'Chefes Posto',
           'Upload Excel'].index(st.session_state['current_page'])
)

# Título da página
st.title("Seja Bem Vindo ao Manipulador Excel - SAEB - SAV - DOS")

# Renderiza a página Home com os botões
if st.session_state['current_page'] == 'Home':
    st.markdown('<div class="button-container">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("CID", key="cid_button"):
            set_page("Produtividade")
            st.rerun()
        st.markdown("""
            <div class="custom-button" onclick="document.getElementById('cid_button').click()">
                <img src="https://img.icons8.com/ios-filled/50/004aad/credit-card.png" alt="Card Icon"/>
                CID
            </div>
        """, unsafe_allow_html=True)

    with col2:
        if st.button("Modificar Excel", key="upload_button"):
            set_page("Upload Excel")
            st.rerun()
        st.markdown("""
            <div class="custom-button" onclick="document.getElementById('upload_button').click()">
                <img src="https://img.icons8.com/ios-filled/50/004aad/upload.png" alt="Upload Icon"/>
                Modificar Excel
            </div>
        """, unsafe_allow_html=True)

    with col3:
        if st.button("Informações", key="info_button"):
            set_page("Informações")
            st.rerun()
        st.markdown("""
            <div class="custom-button" onclick="document.getElementById('info_button').click()">
                <img src="https://img.icons8.com/ios-filled/50/004aad/info.png" alt="Info Icon"/>
                Informações
            </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Renderiza as outras páginas com base na seleção
try:
    if st.session_state['current_page'] == 'Home' and aba != 'Home':
        st.session_state['current_page'] = aba
        st.rerun()
    elif st.session_state['current_page'] == 'Produtividade':
        render_produtividade()
    elif st.session_state['current_page'] == 'Geral Amplo':
        render_geral_amplo()
    elif st.session_state['current_page'] == 'Lista X':
        render_lista_x()
    elif st.session_state['current_page'] == 'Geral Resumo':
        render_geral_resumo()
    elif st.session_state['current_page'] == 'Visitas Realizadas':
        render_visitas_realizadas()
    elif st.session_state['current_page'] == 'Ag. Visita':
        render_ag_visita()
    elif st.session_state['current_page'] == 'Ag. Info Prefeitura':
        render_ag_info_prefeitura()
    elif st.session_state['current_page'] == 'Publicados':
        render_publicados()
    elif st.session_state['current_page'] == 'Ag. Instalação':
        render_ag_instalacao()
    elif st.session_state['current_page'] == 'Instalados':
        render_instalados()
    elif st.session_state['current_page'] == 'Funcionando':
        render_funcionando()
    elif st.session_state['current_page'] == 'Treina Turma':
        render_treina_turma()
    elif st.session_state['current_page'] == 'Treina Cidade':
        render_treina_cidade()
    elif st.session_state['current_page'] == 'Informações':
        render_informacoes()
    elif st.session_state['current_page'] == 'Chefes Posto':
        render_chefes_posto()
    elif st.session_state['current_page'] == 'Upload Excel':
        render_upload_excel()
except Exception as e:
    st.error(f"Erro ao carregar a aba {st.session_state['current_page']}: {str(e)}")
    st.write("Verifique se o arquivo 'ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx' está na raiz do projeto, possui a aba correspondente e contém as colunas esperadas no formato correto.")