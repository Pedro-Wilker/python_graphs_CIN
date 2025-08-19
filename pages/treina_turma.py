import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_treina_turma(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Treina-turma com caching."""
    try:
        raw_df = load_excel('Treina-turma', _file_path)
        df = process_sheet_data(raw_df, 'Treina-turma')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Treina-turma: {str(e)}")
        return pd.DataFrame()

def render_treina_turma(uploaded_file=None):
    st.markdown("""
        <h3>Treina Turma <span class="material-icons" style="vertical-align: middle; color: #004aad;">school</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_treina_turma(file_path)
    
    expected_columns = list(SHEET_CONFIG['Treina-turma']['columns'].keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Treina-turma': {', '.join(missing_columns)}")
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados
    tab1 = st.tabs(["Dados"])[0]
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            periodo_inicio = st.date_input("Período Previsto de Treinamento - Início (opcional)", value=None, key="new_periodo_inicio")
            periodo_fim = st.date_input("Período Previsto de Treinamento - Fim (opcional)", value=None, key="new_periodo_fim")
            turma = st.number_input("Turma", min_value=0, step=1, key="new_turma")
            realizou_treinamento = st.checkbox("Realizou Treinamento?", key="new_realizou_treinamento")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO': periodo_inicio.strftime('%d/%m/%Y') if periodo_inicio else '',
                        'PERÍODO PREVISTO DE TREINAMENTO_FIM': periodo_fim.strftime('%d/%m/%Y') if periodo_fim else '',
                        'TURMA': turma,
                        'REALIZOU TREINAMENTO?': realizou_treinamento
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Treina-turma', file_path):
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
                    periodo_inicio_edit = st.date_input("Período Previsto de Treinamento - Início (opcional)", 
                                                        value=pd.to_datetime(row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO']) and row['PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'] else None,
                                                        key="edit_periodo_inicio")
                    periodo_fim_edit = st.date_input("Período Previsto de Treinamento - Fim (opcional)", 
                                                     value=pd.to_datetime(row['PERÍODO PREVISTO DE TREINAMENTO_FIM'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['PERÍODO PREVISTO DE TREINAMENTO_FIM']) and row['PERÍODO PREVISTO DE TREINAMENTO_FIM'] else None,
                                                     key="edit_periodo_fim")
                    turma_edit = st.number_input("Turma", min_value=0, step=1, value=int(row['TURMA']) if pd.notna(row['TURMA']) else 0, key="edit_turma")
                    realizou_treinamento_edit = st.checkbox("Realizou Treinamento?", value=row['REALIZOU TREINAMENTO?'], key="edit_realizou_treinamento")
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'PERÍODO PREVISTO DE TREINAMENTO_INÍCIO'] = periodo_inicio_edit.strftime('%d/%m/%Y') if periodo_inicio_edit else ''
                            df.at[idx, 'PERÍODO PREVISTO DE TREINAMENTO_FIM'] = periodo_fim_edit.strftime('%d/%m/%Y') if periodo_fim_edit else ''
                            df.at[idx, 'TURMA'] = turma_edit
                            df.at[idx, 'REALIZOU TREINAMENTO?'] = realizou_treinamento_edit
                            if save_excel(df, 'Treina-turma', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Treina-turma', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")