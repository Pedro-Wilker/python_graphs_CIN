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

st.set_page_config(page_title="Análise CIN - Bahia", layout="wide")

st.sidebar.title("Navegação")
aba = st.sidebar.selectbox(
    "Selecione a Aba",
    [
        "Produtividade", "Geral Amplo", "Lista X", "Geral Resumo",
        "Visitas Realizadas", "Ag. Visita", "Ag. Info Prefeitura",
        "Publicados", "Ag. Instalação", "Instalados", "Funcionando",
        "Treina Turma", "Treina Cidade", "Informações", "Chefes Posto",
        "Upload Excel"
    ]
)

st.title("Análise das Produções de CIN das Cidades - Bahia")

try:
    if aba == "Produtividade":
        render_produtividade()
    elif aba == "Geral Amplo":
        render_geral_amplo()
    elif aba == "Lista X":
        render_lista_x()
    elif aba == "Geral Resumo":
        render_geral_resumo()
    elif aba == "Visitas Realizadas":
        render_visitas_realizadas()
    elif aba == "Ag. Visita":
        render_ag_visita()
    elif aba == "Ag. Info Prefeitura":
        render_ag_info_prefeitura()
    elif aba == "Publicados":
        render_publicados()
    elif aba == "Ag. Instalação":
        render_ag_instalacao()
    elif aba == "Instalados":
        render_instalados()
    elif aba == "Funcionando":
        render_funcionando()
    elif aba == "Treina Turma":
        render_treina_turma()
    elif aba == "Treina Cidade":
        render_treina_cidade()
    elif aba == "Informações":
        render_informacoes()
    elif aba == "Chefes Posto":
        render_chefes_posto()
    elif aba == "Upload Excel":
        render_upload_excel()
except Exception as e:
    st.error(f"Erro ao carregar a aba {aba}: {str(e)}")
    st.write("Verifique se o arquivo 'ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx' está na raiz do projeto, possui a aba correspondente e contém as colunas esperadas no formato correto.")