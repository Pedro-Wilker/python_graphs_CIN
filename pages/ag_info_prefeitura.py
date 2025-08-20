import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import EXCEL_FILE, load_excel, process_sheet_data, save_excel, SHEET_CONFIG
import plotly.express as px

@st.cache_data
def load_and_process_ag_info_prefeitura(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag_info_prefeitura com caching."""
    try:
        raw_df = load_excel('Ag_info_prefeitura', _file_path)
        if raw_df.empty:
            st.error("Nenhum dado disponível para a aba 'Ag_info_prefeitura'. Verifique o nome da aba no arquivo Excel.")
            return pd.DataFrame()
        
        # Verificar colunas esperadas
        expected_columns = list(SHEET_CONFIG['Ag_info_prefeitura']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            for col in missing_columns:
                col_type = SHEET_CONFIG['Ag_info_prefeitura']['columns'][col].get('type', 'string')
                if col_type == 'date':
                    raw_df[col] = pd.NaT
                elif col_type == 'categorical':
                    raw_df[col] = ''  # Default to empty string for categorical
                else:
                    raw_df[col] = ''
        
        df = process_sheet_data(raw_df, 'Ag_info_prefeitura')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_info_prefeitura: {str(e)}")
        return pd.DataFrame()

def render_ag_info_prefeitura(uploaded_file=None):
    st.markdown("""
        <h3>Aguardando Informações da Prefeitura <span class="material-icons" style="vertical-align: middle; color: #004aad;">info</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_ag_info_prefeitura(file_path)
    
    if df.empty:
        st.error("Nenhum dado disponível para a aba 'Ag_info_prefeitura'. Verifique o arquivo Excel e o nome da aba.")
        return
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    # Aba de navegação: Dados e Dashboard
    tab1, tab2 = st.tabs(["Dados", "Dashboard"])
    
    with tab1:
        # Adicionar Novo Registro
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            sit_infra = st.selectbox(
                "Situação da Infra-estrutura p/ Visita Técnica",
                SHEET_CONFIG['Ag_info_prefeitura']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                key="new_sit_infra"
            )
            data_visita = st.date_input("Data da Visita Técnica (opcional)", value=None, key="new_data_visita")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': sit_infra,
                        'DATA DA VISITA TÉCNICA': data_visita.strftime('%d/%m/%Y') if data_visita else ''
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Ag_info_prefeitura', file_path):
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
                    sit_infra_values = SHEET_CONFIG['Ag_info_prefeitura']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values']
                    current_sit_infra = row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']
                    default_index = sit_infra_values.index(current_sit_infra) if current_sit_infra in sit_infra_values else 0
                    sit_infra_edit = st.selectbox(
                        "Situação da Infra-estrutura p/ Visita Técnica",
                        sit_infra_values,
                        index=default_index,
                        key="edit_sit_infra"
                    )
                    data_visita_edit = st.date_input(
                        "Data da Visita Técnica (opcional)",
                        value=pd.to_datetime(row['DATA DA VISITA TÉCNICA'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA VISITA TÉCNICA']) and row['DATA DA VISITA TÉCNICA'] else None,
                        key="edit_data_visita"
                    )
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = sit_infra_edit
                            df.at[idx, 'DATA DA VISITA TÉCNICA'] = data_visita_edit.strftime('%d/%m/%Y') if data_visita_edit else ''
                            if save_excel(df, 'Ag_info_prefeitura', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Ag_info_prefeitura', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")
    
    with tab2:
        st.markdown("### Dashboard de Situação da Infra-estrutura")
        # Seletor para limitar o número de cidades
        limite_cidades = st.selectbox(
            "Limitar número de cidades no gráfico",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades"
        )
        
        # Filtrar o DataFrame com base no limite
        df_grafico = df.head(limite_cidades) if limite_cidades != "Sem Limites" else df.copy()
        
        # Mapear valores para as categorias desejadas
        valid_categories = ["Sem pendência", "Com Pendência", "Não Informada"]
        df_grafico['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = df_grafico['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].apply(
            lambda x: x if x in valid_categories else "Não Informada"
        )
        
        # Contar cidades por categoria
        df_counts = df_grafico['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].value_counts().reset_index()
        df_counts.columns = ['Situação', 'Contagem']
        
        # Garantir que todas as categorias estejam presentes, mesmo com contagem 0
        for category in valid_categories:
            if category not in df_counts['Situação'].values:
                df_counts = pd.concat([df_counts, pd.DataFrame({'Situação': [category], 'Contagem': [0]})], ignore_index=True)
        
        # Criar gráfico de pizza
        if not df_counts.empty and df_counts['Contagem'].sum() > 0:
            fig = px.pie(
                df_counts,
                names='Situação',
                values='Contagem',
                title='Distribuição de Cidades por Situação da Infra-estrutura para Visita Técnica',
                height=400,
                color='Situação',
                color_discrete_map={
                    'Sem pendência': '#00CC96',  # Verde
                    'Com Pendência': '#EF553B',  # Vermelho
                    'Não Informada': '#636EFA'   # Azul
                }
            )
            fig.update_traces(
                textinfo='percent+label',
                textposition='inside',
                showlegend=True
            )
            fig.update_layout(
                legend_title_text='Situação',
                margin=dict(t=50, b=50, l=50, r=50)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o gráfico de pizza.")