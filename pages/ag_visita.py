import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_ag_visita(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag. Visita com caching."""
    try:
        raw_df = load_excel('Ag. Visita', _file_path)
        df = process_sheet_data(raw_df, 'Ag. Visita')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag. Visita: {str(e)}")
        return pd.DataFrame()

def render_ag_visita(uploaded_file=None):
    st.markdown("""
        <h3>Aguardando Visita Técnica <span class="material-icons" style="vertical-align: middle; color: #004aad;">engineering</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_ag_visita(file_path)
    
    expected_columns = list(SHEET_CONFIG['Ag. Visita']['columns'].keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Ag. Visita': {', '.join(missing_columns)}")
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados
    tab1 = st.tabs(["Dados"])[0]
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            sit_infra = st.selectbox("Situação da Infra-estrutura p/ Visita Técnica", 
                                     SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                                     key="new_sit_infra")
            data_visita = st.date_input("Data da Visita Técnica (opcional)", value=None, key="new_data_visita")
            parecer_visita = st.selectbox("Parecer da Visita Técnica", 
                                          SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                                          key="new_parecer_visita")
            adequacoes_realizadas = st.checkbox("Adequações Após Visita Técnica Realizadas?", key="new_adequacoes")
            data_finalizacao = st.date_input("Data de Finalização das Adequações (opcional)", value=None, key="new_data_finalizacao")
            previsao_ajuste = st.text_input("Previsão Ajuste Estrutura p/ Visita", key="new_previsao_ajuste")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': sit_infra,
                        'DATA DA VISITA TÉCNICA': data_visita.strftime('%d/%m/%Y') if data_visita else '',
                        'PARECER DA VISITA TÉCNICA': parecer_visita,
                        'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?': adequacoes_realizadas,
                        'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES': data_finalizacao.strftime('%d/%m/%Y') if data_finalizacao else '',
                        'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': previsao_ajuste
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Ag. Visita', file_path):
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
                    cidade_edit = st.text_input("Cidade", value=row['CIDADE'], key="edit_cidade")
                    sit_infra_edit = st.selectbox("Situação da Infra-estrutura p/ Visita Técnica", 
                                                  SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                                                  index=SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'].index(row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']) if row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] in SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'] else 0,
                                                  key="edit_sit_infra")
                    data_visita_edit = st.date_input("Data da Visita Técnica (opcional)", 
                                                     value=pd.to_datetime(row['DATA DA VISITA TÉCNICA'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA VISITA TÉCNICA']) and row['DATA DA VISITA TÉCNICA'] else None,
                                                     key="edit_data_visita")
                    parecer_visita_edit = st.selectbox("Parecer da Visita Técnica", 
                                                       SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                                                       index=SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'].index(row['PARECER DA VISITA TÉCNICA']) if row['PARECER DA VISITA TÉCNICA'] in SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'] else 0,
                                                       key="edit_parecer_visita")
                    adequacoes_realizadas_edit = st.checkbox("Adequações Após Visita Técnica Realizadas?", 
                                                            value=row['ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?'], key="edit_adequacoes")
                    data_finalizacao_edit = st.date_input("Data de Finalização das Adequações (opcional)", 
                                                          value=pd.to_datetime(row['DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES']) and row['DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'] else None,
                                                          key="edit_data_finalizacao")
                    previsao_ajuste_edit = st.text_input("Previsão Ajuste Estrutura p/ Visita", 
                                                         value=row['PREVISÃO AJUSTE ESTRUTURA P/ VISITA'], key="edit_previsao_ajuste")
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = sit_infra_edit
                            df.at[idx, 'DATA DA VISITA TÉCNICA'] = data_visita_edit.strftime('%d/%m/%Y') if data_visita_edit else ''
                            df.at[idx, 'PARECER DA VISITA TÉCNICA'] = parecer_visita_edit
                            df.at[idx, 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?'] = adequacoes_realizadas_edit
                            df.at[idx, 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'] = data_finalizacao_edit.strftime('%d/%m/%Y') if data_finalizacao_edit else ''
                            df.at[idx, 'PREVISÃO AJUSTE ESTRUTURA P/ VISITA'] = previsao_ajuste_edit
                            if save_excel(df, 'Ag. Visita', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Ag. Visita', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")