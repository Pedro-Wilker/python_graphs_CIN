import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_chefes_posto(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Chefes_Posto com caching."""
    try:
        raw_df = load_excel('Chefes_Posto', _file_path)
        df = process_sheet_data(raw_df, 'Chefes_Posto')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Chefes_Posto: {str(e)}")
        return pd.DataFrame()

def render_chefes_posto(uploaded_file=None):
    st.markdown("""
        <h3>Chefes de Posto <span class="material-icons" style="vertical-align: middle; color: #004aad;">person</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_chefes_posto(file_path)
    
    expected_columns = list(SHEET_CONFIG['Chefes_Posto']['columns'].keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Chefes_Posto': {', '.join(missing_columns)}")
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados
    tab1 = st.tabs(["Dados"])[0]
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            posto = st.text_input("Posto", key="new_posto")
            nome = st.text_input("Nome", key="new_nome")
            email = st.text_input("E-mail", key="new_email")
            telefone = st.text_input("Telefone", key="new_telefone")
            turma = st.number_input("Turma", min_value=0, step=1, key="new_turma")
            data_treinamento = st.date_input("Data Treinamento (opcional)", value=None, key="new_data_treinamento")
            usuario = st.text_input("Usuário", key="new_usuario")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade and nome:
                    novo = {
                        'Cidade': cidade,
                        'Posto': posto,
                        'Nome': nome,
                        'E-mail': email,
                        'Telefone': telefone,
                        'Turma': turma,
                        'Data treinamento': data_treinamento.strftime('%d/%m/%Y') if data_treinamento else '',
                        'Usuário': usuario
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Chefes_Posto', file_path):
                        st.cache_data.clear()
                        st.success("Registro adicionado!")
                        st.rerun()
                else:
                    st.error("Cidade e Nome são obrigatórios.")
        
        # Editar ou Apagar Registro
        with st.expander("Editar ou Apagar Registro"):
            if not df.empty:
                idx = st.selectbox("Selecione uma linha", df.index, key="edit_idx")
                row = df.loc[idx]
                
                with st.expander("Editar Registro"):
                    cidade_edit = st.text_input("Cidade", value=row['Cidade'], key="edit_cidade")
                    posto_edit = st.text_input("Posto", value=row['Posto'], key="edit_posto")
                    nome_edit = st.text_input("Nome", value=row['Nome'], key="edit_nome")
                    email_edit = st.text_input("E-mail", value=row['E-mail'], key="edit_email")
                    telefone_edit = st.text_input("Telefone", value=row['Telefone'], key="edit_telefone")
                    turma_edit = st.number_input("Turma", min_value=0, step=1, value=int(row['Turma']) if pd.notna(row['Turma']) else 0, key="edit_turma")
                    data_treinamento_edit = st.date_input("Data Treinamento (opcional)", 
                                                         value=pd.to_datetime(row['Data treinamento'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['Data treinamento']) and row['Data treinamento'] else None,
                                                         key="edit_data_treinamento")
                    usuario_edit = st.text_input("Usuário", value=row['Usuário'], key="edit_usuario")
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit and nome_edit:
                            df.at[idx, 'Cidade'] = cidade_edit
                            df.at[idx, 'Posto'] = posto_edit
                            df.at[idx, 'Nome'] = nome_edit
                            df.at[idx, 'E-mail'] = email_edit
                            df.at[idx, 'Telefone'] = telefone_edit
                            df.at[idx, 'Turma'] = turma_edit
                            df.at[idx, 'Data treinamento'] = data_treinamento_edit.strftime('%d/%m/%Y') if data_treinamento_edit else ''
                            df.at[idx, 'Usuário'] = usuario_edit
                            if save_excel(df, 'Chefes_Posto', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade e Nome são obrigatórios.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Chefes_Posto', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")