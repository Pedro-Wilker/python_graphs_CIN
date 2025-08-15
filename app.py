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

# Estilo CSS para botões e sidebar
st.markdown("""
    <style>
    .carousel-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
        padding: 20px;
    }
    .carousel-card {
        width: 100%;
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
    .carousel-card:hover {
        background-color: #004aad;
        color: white;
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
    }
    .carousel-card .icon {
        font-size: 40px;
        margin-bottom: 10px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        border: 2px solid #004aad;
        background-color: #f0f2f6;
        color: #004aad;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #004aad;
        color: white;
    }
    .st-expander {
        border: 1px solid #004aad;
        border-radius: 8px;
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
    st.rerun()

# Sidebar com navegação estilo PanelMenu
st.sidebar.title("Navegação")
with st.sidebar:
    with st.expander("Análise", expanded=True):
        if st.button("Produtividade", icon=":material/credit_card:"):
            set_page("Produtividade")
        if st.button("Geral Amplo", icon=":material/dashboard:"):
            set_page("Geral Amplo")
        if st.button("Geral Resumo", icon=":material/summarize:"):
            set_page("Geral Resumo")
        if st.button("Lista X", icon=":material/list:"):
            set_page("Lista X")
    with st.expander("Agendamentos"):
        if st.button("Ag. Visita", icon=":material/event:"):
            set_page("Ag. Visita")
        if st.button("Ag. Info Prefeitura", icon=":material/account_balance:"):
            set_page("Ag. Info Prefeitura")
        if st.button("Ag. Instalação", icon=":material/construction:"):
            set_page("Ag. Instalação")
    with st.expander("Status"):
        if st.button("Visitas Realizadas", icon=":material/check_circle:"):
            set_page("Visitas Realizadas")
        if st.button("Publicados", icon=":material/publish:"):
            set_page("Publicados")
        if st.button("Instalados", icon=":material/done_all:"):
            set_page("Instalados")
        if st.button("Funcionando", icon=":material/play_circle:"):
            set_page("Funcionando")
    with st.expander("Treinamento"):
        if st.button("Treina Turma", icon=":material/group:"):
            set_page("Treina Turma")
        if st.button("Treina Cidade", icon=":material/location_city:"):
            set_page("Treina Cidade")
    with st.expander("Outros"):
        if st.button("Informações", icon=":material/info:"):
            set_page("Informações")
        if st.button("Chefes Posto", icon=":material/person:"):
            set_page("Chefes Posto")
        if st.button("Upload Excel", icon=":material/upload_file:"):
            set_page("Upload Excel")

# Título da página
st.title("Seja Bem Vindo ao Manipulador Excel - SAEB - SAV - DOS")

# Renderiza a página Home com botões em estilo carousel
if st.session_state['current_page'] == 'Home':
    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
    
    # Botões principais em um grid responsivo
    buttons = [
        ("CID", "Produtividade", ":material/credit_card:"),
        ("Modificar Excel", "Upload Excel", ":material/upload_file:"),
        ("Informações", "Informações", ":material/info:")
    ]
    
    for i in range(0, len(buttons), 3):
        cols = st.columns(3)
        for j, (label, page, icon) in enumerate(buttons[i:i+3]):
            with cols[j if j < len(cols) else 0]:
                if st.button(label, icon=icon, key=f"{page}_button"):
                    set_page(page)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Renderiza as outras páginas com base na seleção
try:
    if st.session_state['current_page'] == 'Home' and st.sidebar.selectbox("Selecione a Aba", ["Home"], index=0, key="home_select") != 'Home':
        set_page(st.sidebar.selectbox("Selecione a Aba", ["Home"], index=0, key="home_select"))
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