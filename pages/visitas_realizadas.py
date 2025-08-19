import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_visitas_realizadas(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Visitas Realizadas com caching."""
    try:
        raw_df = load_excel('Visitas Realizadas', _file_path)
        df = process_sheet_data(raw_df, 'Visitas Realizadas')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Visitas Realizadas: {str(e)}")
        return pd.DataFrame()

def render_visitas_realizadas(uploaded_file=None):
    st.markdown("""
        <h3>Visitas Realizadas <span class="material-icons" style="vertical-align: middle; color: #004aad;">visibility</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_visitas_realizadas(file_path)
    
    expected_columns = list(SHEET_CONFIG['Visitas Realizadas']['columns'].keys())
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        st.warning(f"Colunas ausentes na aba 'Visitas Realizadas': {', '.join(missing_columns)}")
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados
    tab1 = st.tabs(["Dados"])[0]
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            data_visita = st.date_input("Data da Visita (opcional)", value=None, key="new_data_visita")
            parecer_visita = st.selectbox("Parecer da Visita Técnica", 
                                          SHEET_CONFIG['Visitas Realizadas']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                                          key="new_parecer_visita")
            apto_instalacao = st.checkbox("Apto para Instalação?", key="new_apto_instalacao")
            observacao = st.text_area("Observação (opcional)", key="new_observacao")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'DATA DA VISITA': data_visita.strftime('%d/%m/%Y') if data_visita else '',
                        'PARECER DA VISITA TÉCNICA': parecer_visita,
                        'APTO PARA INSTALAÇÃO?': apto_instalacao,
                        'OBSERVAÇÃO': observacao
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Visitas Realizadas', file_path):
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
                    data_visita_edit = st.date_input("Data da Visita (opcional)", 
                                                     value=pd.to_datetime(row['DATA DA VISITA'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA VISITA']) and row['DATA DA VISITA'] else None,
                                                     key="edit_data_visita")
                    parecer_visita_edit = st.selectbox("Parecer da Visita Técnica", 
                                                       SHEET_CONFIG['Visitas Realizadas']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                                                       index=SHEET_CONFIG['Visitas Realizadas']['columns']['PARECER DA VISITA TÉCNICA']['values'].index(row['PARECER DA VISITA TÉCNICA']) if row['PARECER DA VISITA TÉCNICA'] in SHEET_CONFIG['Visitas Realizadas']['columns']['PARECER DA VISITA TÉCNICA']['values'] else 0,
                                                       key="edit_parecer_visita")
                    apto_instalacao_edit = st.checkbox("Apto para Instalação?", value=row['APTO PARA INSTALAÇÃO?'], key="edit_apto_instalacao")
                    observacao_edit = st.text_area("Observação (opcional)", value=row['OBSERVAÇÃO'] if pd.notna(row['OBSERVAÇÃO']) else '', key="edit_observacao")
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'DATA DA VISITA'] = data_visita_edit.strftime('%d/%m/%Y') if data_visita_edit else ''
                            df.at[idx, 'PARECER DA VISITA TÉCNICA'] = parecer_visita_edit
                            df.at[idx, 'APTO PARA INSTALAÇÃO?'] = apto_instalacao_edit
                            df.at[idx, 'OBSERVAÇÃO'] = observacao_edit
                            if save_excel(df, 'Visitas Realizadas', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Visitas Realizadas', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")