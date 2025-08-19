import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_lista_x(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Lista X com caching."""
    try:
        raw_df = load_excel('Lista X', _file_path)
        df = process_sheet_data(raw_df, 'Lista X')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Lista X: {str(e)}")
        return pd.DataFrame()

def render_lista_x(uploaded_file=None):
    st.markdown("""
        <h3>Lista X <span class="material-icons" style="vertical-align: middle; color: #004aad;">list</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_lista_x(file_path)
    
    expected_columns = list(SHEET_CONFIG['Lista X']['columns'].keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Lista X': {', '.join(missing_columns)}")
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados
    tab1 = st.tabs(["Dados"])[0]
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            nao_informou = st.checkbox("Não Informou a Estrutura do Posto", key="new_nao_informou")
            com_pendencia = st.checkbox("Com Pendência na Estrutura do Posto", key="new_com_pendencia")
            sem_pendencia = st.checkbox("Sem Pendência na Estrutura do Posto", key="new_sem_pendencia")
            sanou_pendencias = st.checkbox("Sanou Pendências Indicadas", key="new_sanou_pendencias")
            ag_visita = st.checkbox("Ag. Visita Técnica", key="new_ag_visita")
            parecer_visita = st.selectbox("Parecer da Visita Técnica", 
                                          SHEET_CONFIG['Lista X']['columns']['Parecer da visita técnica']['values'],
                                          key="new_parecer_visita")
            realizou_treinamento = st.checkbox("Realizou Treinamento", key="new_realizou_treinamento")
            ag_publicacao = st.checkbox("Ag. Publicação no Diário Oficial Estado", key="new_ag_publicacao")
            publicado_do = st.checkbox("Publicado no Diário Oficial do Estado", key="new_publicado_do")
            aguardando_instalacao = st.checkbox("Aguardando Instalação", key="new_aguardando_instalacao")
            instalado = st.checkbox("Instalado", key="new_instalado")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'Cidade': cidade,
                        'Não Informou a estrutura do posto': nao_informou,
                        'Com Pendência na estrutura do posto': com_pendencia,
                        'Sem pendência na estrutura do posto': sem_pendencia,
                        'Sanou pendências indicadas': sanou_pendencias,
                        'Ag. Visita técnica': ag_visita,
                        'Parecer da visita técnica': parecer_visita,
                        'Realizou Treinamento': realizou_treinamento,
                        'Ag. Publicação no Diário Oficial Estado': ag_publicacao,
                        'Publicado no Diário Oficial do Estado': publicado_do,
                        'Aguardando instalação': aguardando_instalacao,
                        'instalado': instalado
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Lista X', file_path):
                        st.cache_data.clear()
                        st.success("Registro adicionado!")
                        st.rerun()
                else:
                    st.error("Cidade é obrigatória.")
        
        # Editar ou Apagar Registro
        with st.expander("Editar ou Apagar Registro"):
            if not df.empty:
                idx = st.selectbox("Selecione uma linha", df.index, key="edit_idx")
                row = df.loc[idx]
                
                with st.expander("Editar Registro"):
                    cidade_edit = st.text_input("Cidade", value=row['Cidade'], key="edit_cidade")
                    nao_informou_edit = st.checkbox("Não Informou a Estrutura do Posto", value=row['Não Informou a estrutura do posto'], key="edit_nao_informou")
                    com_pendencia_edit = st.checkbox("Com Pendência na Estrutura do Posto", value=row['Com Pendência na estrutura do posto'], key="edit_com_pendencia")
                    sem_pendencia_edit = st.checkbox("Sem Pendência na Estrutura do Posto", value=row['Sem pendência na estrutura do posto'], key="edit_sem_pendencia")
                    sanou_pendencias_edit = st.checkbox("Sanou Pendências Indicadas", value=row['Sanou pendências indicadas'], key="edit_sanou_pendencias")
                    ag_visita_edit = st.checkbox("Ag. Visita Técnica", value=row['Ag. Visita técnica'], key="edit_ag_visita")
                    parecer_visita_edit = st.selectbox("Parecer da Visita Técnica", 
                                                       SHEET_CONFIG['Lista X']['columns']['Parecer da visita técnica']['values'],
                                                       index=SHEET_CONFIG['Lista X']['columns']['Parecer da visita técnica']['values'].index(row['Parecer da visita técnica']) if row['Parecer da visita técnica'] in SHEET_CONFIG['Lista X']['columns']['Parecer da visita técnica']['values'] else 0,
                                                       key="edit_parecer_visita")
                    realizou_treinamento_edit = st.checkbox("Realizou Treinamento", value=row['Realizou Treinamento'], key="edit_realizou_treinamento")
                    ag_publicacao_edit = st.checkbox("Ag. Publicação no Diário Oficial Estado", value=row['Ag. Publicação no Diário Oficial Estado'], key="edit_ag_publicacao")
                    publicado_do_edit = st.checkbox("Publicado no Diário Oficial do Estado", value=row['Publicado no Diário Oficial do Estado'], key="edit_publicado_do")
                    aguardando_instalacao_edit = st.checkbox("Aguardando Instalação", value=row['Aguardando instalação'], key="edit_aguardando_instalacao")
                    instalado_edit = st.checkbox("Instalado", value=row['instalado'], key="edit_instalado")
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'Cidade'] = cidade_edit
                            df.at[idx, 'Não Informou a estrutura do posto'] = nao_informou_edit
                            df.at[idx, 'Com Pendência na estrutura do posto'] = com_pendencia_edit
                            df.at[idx, 'Sem pendência na estrutura do posto'] = sem_pendencia_edit
                            df.at[idx, 'Sanou pendências indicadas'] = sanou_pendencias_edit
                            df.at[idx, 'Ag. Visita técnica'] = ag_visita_edit
                            df.at[idx, 'Parecer da visita técnica'] = parecer_visita_edit
                            df.at[idx, 'Realizou Treinamento'] = realizou_treinamento_edit
                            df.at[idx, 'Ag. Publicação no Diário Oficial Estado'] = ag_publicacao_edit
                            df.at[idx, 'Publicado no Diário Oficial do Estado'] = publicado_do_edit
                            df.at[idx, 'Aguardando instalação'] = aguardando_instalacao_edit
                            df.at[idx, 'instalado'] = instalado_edit
                            if save_excel(df, 'Lista X', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Lista X', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")