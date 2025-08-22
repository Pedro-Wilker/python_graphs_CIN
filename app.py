import streamlit as st
from streamlit_option_menu import option_menu
from utils import dashboard_utils

# Configurar o Streamlit para desativar a sidebar multipáginas automática
st.set_page_config(
    page_title="Sistema de Acompanhamento do SAC",
    layout="wide",
    initial_sidebar_state="collapsed"  # Colapsa a sidebar padrão, mas usaremos a personalizada
)

# Importações com tratamento de erro
try:
    from pages import (
        geral_amplo, informacoes, treina_turma, treina_cidade, produtividade,
        ag_info_prefeitura, ag_instalacao, ag_visita, chefes_posto, funcionando,
        geral_resumo, instalados, lista_x, publicados, servicos_a_revisar,
        upload_excel, visitas_realizadas
    )
except ImportError as e:
    st.error(f" AscError ao importar módulos do pacote 'pages': {str(e)}")
    st.markdown("""
    ### Possíveis Soluções
    - Verifique se todos os arquivos .py estão presentes em `C:\\Users\\re049227\\Documents\\pythonGraphs\\pages\\`.
    - Confirme que os nomes dos arquivos correspondem exatamente aos importados (ex.: `visitas_realizadas.py`, `dashboard_utils.py`).
    - Execute `dir C:\\Users\\re049227\\Documents\\pythonGraphs\\pages\\` para listar os arquivos.
    """)
    st.stop()

# Inicializar estado da sessão
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'Home'

def set_page(page):
    if st.session_state['current_page'] != page:
        st.session_state['current_page'] = page
        # st.rerun()  # Comentado para evitar recarregamentos

# Sidebar interativa (única a ser exibida)
with st.sidebar:
    page = option_menu(
        "Menu",
        [
            "Home", "Ag_info_prefeitura", "Ag_instalacao", "Ag_visita", "Chefes_Posto",
            "Funcionando", "Geral_Amplo", "Geral_Resumo", "Informações", "Instalados",
            "Lista_X", "Produtividade", "Publicados", "Servicos_a_revisar", "Treina_Cidade",
            "Treina_Turma", "Upload_Excel", "Visita_Realizadas", "Dashboard_Central"
        ],
        icons=["house"] + ["list-task"] * 18,
        menu_icon="cast",
        default_index=0,
        key="menu"
    )
    set_page(page)

# Tela inicial
if st.session_state['current_page'] == "Home":
    st.markdown("""
        <h2>Bem-vindo ao Sistema de Acompanhamento do SAC <span class="material-icons" style="vertical-align: middle; color: #004aad;">dashboard</span></h2>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        ### Sobre a SAEB
        A **Secretaria de Administração do Estado da Bahia (SAEB)** é responsável pela gestão administrativa do estado, abrangendo planejamento, orçamento, gestão de recursos humanos e modernização dos serviços públicos. Seu objetivo é garantir eficiência e transparência na administração pública baiana.
        
        ### Sobre o SAC
        O **Serviço de Atendimento ao Cidadão (SAC)** é uma rede de unidades que oferece serviços públicos de forma integrada, como emissão de documentos (RG, CPF, Carteira de Trabalho), atendimentos previdenciários e serviços de utilidade pública, facilitando o acesso do cidadão a esses serviços.
        
        ### Equipe DOS do SAC
        A **Diretoria de Operações do SAC (DOS)** gerencia as operações das unidades SAC, assegurando a qualidade no atendimento, a implementação de melhorias operacionais e a coordenação das atividades para atender às demandas dos cidadãos com eficiência.
        
        ### Equipe de Carta de Serviços
        A **equipe de Carta de Serviços** é responsável por elaborar e manter a **Carta de Serviços ao Cidadão**, um documento que detalha os serviços oferecidos pelo SAC, incluindo prazos, formas de acesso e canais de atendimento. Essa iniciativa visa promover transparência e facilitar o acesso aos serviços públicos, em conformidade com:
        - **Lei Federal nº 13.460/2017**: Dispõe sobre a participação, proteção e defesa dos direitos do usuário dos serviços públicos, estabelecendo normas para a elaboração da Carta de Serviços.
        - **Decreto Estadual nº 18.771/2019**: Regulamenta a Carta de Serviços ao Cidadão no âmbito do estado da Bahia, definindo diretrizes para sua implementação e atualização.
    """, unsafe_allow_html=True)

# Navegação para outras páginas com tratamento de erro
else:
    try:
        if st.session_state['current_page'] == "Geral_Amplo":
            geral_amplo.render_geral_amplo()
        elif st.session_state['current_page'] == "Informações":
            informacoes.render_informacoes()
        elif st.session_state['current_page'] == "Treina_Turma":
            treina_turma.render_treina_turma()
        elif st.session_state['current_page'] == "Treina_Cidade":
            treina_cidade.render_treina_cidade()
        elif st.session_state['current_page'] == "Produtividade":
            produtividade.render_produtividade()
        elif st.session_state['current_page'] == "Ag_info_prefeitura":
            ag_info_prefeitura.render_ag_info_prefeitura()
        elif st.session_state['current_page'] == "Ag_instalacao":
            ag_instalacao.render_ag_instalacao()
        elif st.session_state['current_page'] == "Ag_visita":
            ag_visita.render_ag_visita()
        elif st.session_state['current_page'] == "Chefes_Posto":
            chefes_posto.render_chefes_posto()
        elif st.session_state['current_page'] == "Funcionando":
            funcionando.render_funcionando()
        elif st.session_state['current_page'] == "Geral_Resumo":
            geral_resumo.render_geral_resumo()
        elif st.session_state['current_page'] == "Instalados":
            instalados.render_instalados()
        elif st.session_state['current_page'] == "Lista_X":
            lista_x.render_lista_x()
        elif st.session_state['current_page'] == "Publicados":
            publicados.render_publicados()
        elif st.session_state['current_page'] == "Servicos_a_revisar":
            servicos_a_revisar.render_servicos_a_revisar()
        elif st.session_state['current_page'] == "Upload_Excel":
            upload_excel.render_upload_excel()
        elif st.session_state['current_page'] == "Visita_Realizadas":
            visitas_realizadas.render_visitas_realizadas()
        elif st.session_state['current_page'] == "Dashboard_Central":
            dashboard_utils.render_dashboard_utils()  # Atualizado para refletir o novo nome da função
    except Exception as e:
        st.error(f"Erro ao renderizar a página {st.session_state['current_page']}: {str(e)}")
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `{page}.py` existe em `C:\\Users\\re049227\\Documents\\pythonGraphs\\pages\\`.
        - Confirme se a função `render_{page.lower()}` está definida no arquivo.
        """)