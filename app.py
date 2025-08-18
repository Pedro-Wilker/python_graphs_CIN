import streamlit as st
from streamlit_option_menu import option_menu
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
from pages.servicos_a_revisar import main as render_servicos_a_revisar  # NOVO IMPORT

# Configuração inicial da página
st.set_page_config(page_title="Manipulador Excel - SAEB - SAV - DOS", layout="wide")

# Adicionar logo (comente até corrigir o caminho da imagem)
# st.logo("C:/Users/re049227/Documents/pythonGraphs/logo.png", size="medium")

# Estilo CSS atualizado para sidebar, carousel e botões
st.markdown("""
    <link rel="stylesheet" href="https://fonts.googleapis.com/icon?family=Material+Icons">
    <style>
    .carousel-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 20px;
        padding: 20px;
    }
    .carousel-card {
        width: 100%;
        height: 180px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        border-radius: 12px;
        border: 2px solid #004aad;
        background-color: #f0f2f6;
        color: #004aad;
        font-size: 16px;
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
        font-size: 36px;
        margin-bottom: 8px;
    }
    .carousel-card .description {
        font-size: 12px;
        font-weight: normal;
        color: #333;
        margin-top: 5px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        border: 2px solid #004aad;
        background-color: #f0f2f6;
        color: #004aad;
        font-weight: bold;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #004aad;
        color: white;
    }
    .st-spinner {
        border: 2px solid #004aad;
        border-top: 2px solid #f0f2f6;
        border-radius: 50%;
        width: 24px;
        height: 24px;
        animation: spin 1s linear infinite;
        margin: auto;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .sidebar .sidebar-content {
        background-color: #f0f2f6;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa o estado da sessão para controle de navegação
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

# Função para atualizar a página atual
def set_page(page):
    if st.session_state['current_page'] != page:
        with st.spinner("Carregando página..."):
            st.session_state['current_page'] = page
            st.rerun()

# Configuração do menu na sidebar com streamlit-option-menu
with st.sidebar:
    st.title("Manipulador Excel")
    st.markdown("""
        <h3>SAEB - SAV - DOS <span class="material-icons" style="vertical-align: middle; color: #004aad;">business</span></h3>
    """, unsafe_allow_html=True)
    
    selected = option_menu(
        menu_title=None,
        options=[
            "Home",
            "Análise",
            "Produtividade",
            "Geral Amplo",
            "Geral Resumo",
            "Lista X",
            "Agendamentos",
            "Ag. Visita",
            "Ag. Info Prefeitura",
            "Ag. Instalação",
            "Status",
            "Visitas Realizadas",
            "Publicados",
            "Instalados",
            "Funcionando",
            "Treinamento",
            "Treina Turma",
            "Treina Cidade",
            "Outros",
            "Serviços a Revisar",  # NOVA OPÇÃO
            "Informações",
            "Chefes Posto",
            "Upload Excel",
            "Ajuda"
        ],
        icons=[
            "house",
            "bar-chart",
            "credit-card",
            "dashboard",
            "summarize",
            "list",
            "calendar",
            "event",
            "account-balance",
            "construction",
            "check-circle",
            "check-circle",
            "publish",
            "done-all",
            "play-circle",
            "school",
            "group",
            "location-city",
            "assignment",  # ÍCONE PARA SERVIÇOS A REVISAR
            "info",
            "person",
            "upload-file",
            "question-circle"
        ],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#004aad", "font-size": "20px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#004aad",
                "color": "#004aad"
            },
            "nav-link-selected": {"background-color": "#004aad", "color": "white"},
        }
    )

    page_mapping = {
        "Home": "Home",
        "Produtividade": "Produtividade",
        "Geral Amplo": "Geral Amplo",
        "Geral Resumo": "Geral Resumo",
        "Lista X": "Lista X",
        "Ag. Visita": "Ag. Visita",
        "Ag. Info Prefeitura": "Ag. Info Prefeitura",
        "Ag. Instalação": "Ag. Instalação",
        "Visitas Realizadas": "Visitas Realizadas",
        "Publicados": "Publicados",
        "Instalados": "Instalados",
        "Funcionando": "Funcionando",
        "Treina Turma": "Treina Turma",
        "Treina Cidade": "Treina Cidade",
        "Serviços a Revisar": "Serviços a Revisar",  # NOVO MAPEAMENTO
        "Informações": "Informações",
        "Chefes Posto": "Chefes Posto",
        "Upload Excel": "Upload Excel",
        "Ajuda": "Ajuda"
    }

    if selected not in ["Análise", "Agendamentos", "Status", "Treinamento", "Outros"]:
        set_page(page_mapping.get(selected, "Home"))

# Título da página com subheader
st.title("Manipulador Excel - SAEB - SAV - DOS")
st.subheader("Visualize e gerencie os dados do acompanhamento CIN em todo lugar")

# Renderiza a página Home com carousel
if st.session_state['current_page'] == 'Home':
    st.markdown("""
        <h3>Bem-vindo ao Sistema <span class="material-icons" style="vertical-align: middle; color: #004aad;">home</span></h3>
    """, unsafe_allow_html=True)
    st.markdown("Selecione uma opção abaixo para começar a explorar os dados.")
    
    st.markdown('<div class="carousel-container">', unsafe_allow_html=True)
    
    buttons = [
        ("CID", "Produtividade", ":material/credit_card:", "Analise a produtividade por cidade e mês"),
        ("Modificar Excel", "Upload Excel", ":material/upload_file:", "Faça upload de novos arquivos Excel"),
        ("Informações", "Informações", ":material/info:", "Consulte informações detalhadas das cidades")
    ]
    
    for i in range(0, len(buttons), 3):
        cols = st.columns(3)
        for j, (label, page, icon, description) in enumerate(buttons[i:i+3]):
            with cols[j if j < len(cols) else 0]:
                st.markdown(
                    f"""
                    <div class="carousel-card" onclick="window.location.href='#{page}'">
                        <span class="icon">{icon}</span>
                        {label}
                        <div class="description">{description}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if st.button(label, key=f"{page}_button"):
                    set_page(page)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Página de Ajuda
elif st.session_state['current_page'] == 'Ajuda':
    st.markdown("""
        <h3>Ajuda e Suporte <span class="material-icons" style="vertical-align: middle; color: #004aad;">question_circle</span></h3>
    """, unsafe_allow_html=True)
    st.markdown("""
    ### Bem-vindo ao Manipulador Excel - SAEB - SAV - DOS
    Este sistema permite visualizar e gerenciar os dados do arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx`.

    #### Como Navegar
    - **Sidebar**: Use o menu à esquerda para acessar diferentes seções do sistema.
    - **Home**: Acesse as principais funcionalidades através dos cartões interativos.
    - **Análise**: Visualize dados de produtividade, resumos e listas detalhadas.
    - **Agendamentos**: Consulte informações sobre visitas técnicas, instalações e dados das prefeituras.
    - **Status**: Veja o progresso de visitas realizadas, publicações e instalações concluídas.
    - **Treinamento**: Acesse informações sobre turmas e cidades treinadas.
    - **Outros**: Consulte informações detalhadas, chefes de posto ou faça upload de novos arquivos Excel.

    #### Dicas
    - **Atualizar Dados**: Na página "Informações", use o botão "Atualizar Dados" para recarregar o arquivo Excel.
    - **Filtros**: Use os campos de busca e seletores para filtrar dados nas páginas.
    - **Gráficos**: Explore os gráficos interativos na página "Produtividade" para análises detalhadas.
    - **Responsividade**: O sistema é otimizado para diferentes tamanhos de tela.

    #### Solução de Problemas
    - **Erro ao carregar dados**: Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está no diretório `C:\\Users\\re049227\\Documents\\pythonGraphs\\` e contém as abas e colunas esperadas.
    - **Dados ausentes**: Certifique-se de que as colunas como `PREVISÃO AJUSTE ESTRUTURA P/ VISITA` e `PENDÊNCIA P/ VISITA TÉCNICA` estão formatadas corretamente.
    - **Contato**: Para suporte, entre em contato com a equipe de desenvolvimento.

    #### Sobre
    Este sistema foi desenvolvido para facilitar a análise e gestão de dados do projeto CIN, com foco em usabilidade e desempenho.
    """)

# Renderiza as outras páginas com base na seleção
else:
    try:
        with st.spinner("Carregando dados..."):
            st.write(f"DEBUG: Tentando carregar página {st.session_state['current_page']}")
            if st.session_state['current_page'] == 'Produtividade':
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
            elif st.session_state['current_page'] == 'Serviços a Revisar':
                render_servicos_a_revisar()
            elif st.session_state['current_page'] == 'Informações':
                render_informacoes()
            elif st.session_state['current_page'] == 'Chefes Posto':
                render_chefes_posto()
            elif st.session_state['current_page'] == 'Upload Excel':
                render_upload_excel()
    except Exception as e:
        st.error(f"Erro ao carregar a aba {st.session_state['current_page']}: {str(e)}")
        st.write("Detalhes do erro:", exc_info=True)
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está no diretório `C:\\Users\\re049227\\Documents\\pythonGraphs\\`.
        - Confirme se a aba correspondente existe no arquivo Excel.
        - Assegure-se de que as colunas esperadas estão presentes e formatadas corretamente.
        - Consulte a seção **Ajuda** na sidebar para mais informações.
        """)