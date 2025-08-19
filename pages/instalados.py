import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_instalados(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Instalados com caching."""
    try:
        raw_df = load_excel('Instalados', _file_path)
        df = process_sheet_data(raw_df, 'Instalados')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Instalados: {str(e)}")
        return pd.DataFrame()

def render_instalados(uploaded_file=None):
    st.markdown("""
        <h3>Instalados <span class="material-icons" style="vertical-align: middle; color: #004aad;">check_circle</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_instalados(file_path)
    
    expected_columns = list(SHEET_CONFIG['Instalados']['columns'].keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Instalados': {', '.join(missing_columns)}")
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados
    tab1 = st.tabs(["Dados"])[0]
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            parecer_visita = st.selectbox("Parecer da Visita Técnica", 
                                          SHEET_CONFIG['Instalados']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                                          key="new_parecer_visita")
            periodo_inicio = st.date_input("Período Previsto de Treinamento - Início (opcional)", value=None, key="new_periodo_inicio")
            periodo_fim = st.date_input("Período Previsto de Treinamento - Fim (opcional)", value=None, key="new_periodo_fim")
            situacao_termo = st.text_input("Situação do Novo Termo de Cooperação", key="new_situacao_termo")
            data_do = st.date_input("Data do D.O. (opcional)", value=None, key="new_data_do")
            apto_instalacao = st.checkbox("Apto para Instalação?", key="new_apto_instalacao")
            data_instalacao = st.date_input("Data da Instalação (opcional)", value=None, key="new_data_instalacao")
            data_inicio_atend = st.date_input("Data do Início Atend. (opcional)", value=None, key="new_data_inicio_atend")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'PARECER DA VISITA TÉCNICA': parecer_visita,
                        'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO': periodo_inicio.strftime('%d/%m/%Y') if periodo_inicio else '',
                        'PERÍODO PREVISTO DE TREINAMENTO_FIM': periodo_fim.strftime('%d/%m/%Y') if periodo_fim else '',
                        'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': situacao_termo,
                        'DATA DO D.O.': data_do.strftime('%d/%m/%Y') if data_do else '',
                        'APTO PARA INSTALAÇÃO?': apto_instalacao,
                        'DATA DA INSTALAÇÃO': data_instalacao.strftime('%d/%m/%Y') if data_instalacao else '',
                        'DATA DO INÍCIO ATEND.': data_inicio_atend.strftime('%d/%m/%Y') if data_inicio_atend else ''
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Instalados', file_path):
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
                    parecer_visita_edit = st.selectbox("Parecer da Visita Técnica", 
                                                       SHEET_CONFIG['Instalados']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                                                       index=SHEET_CONFIG['Instalados']['columns']['PARECER DA VISITA TÉCNICA']['values'].index(row['PARECER DA VISITA TÉCNICA']) if row['PARECER DA VISITA TÉCNICA'] in SHEET_CONFIG['Instalados']['columns']['PARECER DA VISITA TÉCNICA']['values'] else 0,
                                                       key="edit_parecer_visita")
                    periodo_inicio_edit = st.date_input("Período Previsto de Treinamento - Início (opcional)", 
                                                        value=pd.to_datetime(row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO']) and row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'] else None,
                                                        key="edit_periodo_inicio")
                    periodo_fim_edit = st.date_input("Período Previsto de Treinamento - Fim (opcional)", 
                                                     value=pd.to_datetime(row['PERÍODO PREVISTO DE TREINAMENTO_FIM'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['PERÍODO PREVISTO DE TREINAMENTO_FIM']) and row['PERÍODO PREVISTO DE TREINAMENTO_FIM'] else None,
                                                     key="edit_periodo_fim")
                    situacao_termo_edit = st.text_input("Situação do Novo Termo de Cooperação", value=row['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO'], key="edit_situacao_termo")
                    data_do_edit = st.date_input("Data do D.O. (opcional)", 
                                                 value=pd.to_datetime(row['DATA DO D.O.'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DO D.O.']) and row['DATA DO D.O.'] else None,
                                                 key="edit_data_do")
                    apto_instalacao_edit = st.checkbox("Apto para Instalação?", value=row['APTO PARA INSTALAÇÃO?'], key="edit_apto_instalacao")
                    data_instalacao_edit = st.date_input("Data da Instalação (opcional)", 
                                                        value=pd.to_datetime(row['DATA DA INSTALAÇÃO'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA INSTALAÇÃO']) and row['DATA DA INSTALAÇÃO'] else None,
                                                        key="edit_data_instalacao")
                    data_inicio_atend_edit = st.date_input("Data do Início Atend. (opcional)", 
                                                          value=pd.to_datetime(row['DATA DO INÍCIO ATEND.'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DO INÍCIO ATEND.']) and row['DATA DO INÍCIO ATEND.'] else None,
                                                          key="edit_data_inicio_atend")
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'PARECER DA VISITA TÉCNICA'] = parecer_visita_edit
                            df.at[idx, 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'] = periodo_inicio_edit.strftime('%d/%m/%Y') if periodo_inicio_edit else ''
                            df.at[idx, 'PERÍODO PREVISTO DE TREINAMENTO_FIM'] = periodo_fim_edit.strftime('%d/%m/%Y') if periodo_fim_edit else ''
                            df.at[idx, 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO'] = situacao_termo_edit
                            df.at[idx, 'DATA DO D.O.'] = data_do_edit.strftime('%d/%m/%Y') if data_do_edit else ''
                            df.at[idx, 'APTO PARA INSTALAÇÃO?'] = apto_instalacao_edit
                            df.at[idx, 'DATA DA INSTALAÇÃO'] = data_instalacao_edit.strftime('%d/%m/%Y') if data_instalacao_edit else ''
                            df.at[idx, 'DATA DO INÍCIO ATEND.'] = data_inicio_atend_edit.strftime('%d/%m/%Y') if data_inicio_atend_edit else ''
                            if save_excel(df, 'Instalados', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Instalados', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")