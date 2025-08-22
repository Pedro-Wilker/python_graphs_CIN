import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
from python_graphs_CIN.utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE

@st.cache_data
def load_and_process_ag_visita(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag. Visita com caching."""
    try:
        raw_df = load_excel('Ag. Visita', _file_path)
        if raw_df.empty:
            st.error("Nenhum dado disponível para a aba 'Ag. Visita'. Verifique o nome da aba no arquivo Excel.")
            return pd.DataFrame()
        
        df = process_sheet_data(raw_df, 'Ag. Visita')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag. Visita: {str(e)}")
        return pd.DataFrame()

def generate_ag_visita_dashboards(df, limite_cidades="Sem Limites"):
    """Gera gráficos para a aba 'Ag. Visita'."""
    if df.empty:
        return []
    
    df_plot = df.head(limite_cidades) if isinstance(limite_cidades, int) else df
    figs = []
    
    # Gráfico 1: Distribuição por Situação da Infra-estrutura
    sit_infra_counts = df_plot['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].value_counts().reset_index()
    sit_infra_counts.columns = ['Situação', 'Quantidade']
    fig1 = px.pie(
        sit_infra_counts,
        values='Quantidade',
        names='Situação',
        title='Distribuição por Situação da Infra-estrutura',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig1.update_traces(textinfo='percent+label')
    figs.append(fig1)
    
    # Gráfico 2: Distribuição por Parecer da Visita Técnica
    parecer_counts = df_plot['PARECER DA VISITA TÉCNICA'].value_counts().reset_index()
    parecer_counts.columns = ['Parecer', 'Quantidade']
    fig2 = px.bar(
        parecer_counts,
        x='Parecer',
        y='Quantidade',
        title='Distribuição por Parecer da Visita Técnica',
        text='Quantidade',
        color='Parecer',
        color_discrete_sequence=px.colors.qualitative.Plotly
    )
    fig2.update_traces(textposition='outside')
    fig2.update_layout(showlegend=False)
    figs.append(fig2)
    
    # Gráfico 3: Visitas por Data
    df_data = df_plot[df_plot['DATA DA VISITA TÉCNICA'].notna() & (df_plot['DATA DA VISITA TÉCNICA'] != '')]
    if not df_data.empty:
        df_data['DATA'] = pd.to_datetime(df_data['DATA DA VISITA TÉCNICA'], format='%d/%m/%Y', errors='coerce')
        df_data = df_data[df_data['DATA'].notna()]
        df_data['Mês-Ano'] = df_data['DATA'].dt.strftime('%Y-%m')
        data_counts = df_data['Mês-Ano'].value_counts().sort_index().reset_index()
        data_counts.columns = ['Mês-Ano', 'Quantidade']
        fig3 = px.line(
            data_counts,
            x='Mês-Ano',
            y='Quantidade',
            title='Visitas Técnicas por Mês',
            markers=True,
            text='Quantidade'
        )
        fig3.update_traces(mode='lines+markers+text', textposition='top center')
        fig3.update_layout(xaxis_title="Mês-Ano", yaxis_title="Número de Visitas")
        figs.append(fig3)
    
    return figs

def render_ag_visita(uploaded_file=None):
    st.markdown("""
        <h3>Aguardando Visita Técnica <span class="material-icons" style="vertical-align: middle; color: #004aad;">engineering</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_ag_visita(file_path)
    
    if df.empty:
        st.error("Nenhum dado disponível para a aba 'Ag. Visita'. Verifique o arquivo Excel e o nome da aba.")
        return
    
    st.markdown("### Tabela Completa")
    st.dataframe(df, use_container_width=True)
    
    tab1, tab2 = st.tabs(["Dados", "Dashboard"])
    
    with tab1:
        with st.expander("Adicionar Novo Registro"):
            cidade = st.text_input("Cidade", key="new_cidade")
            sit_infra = st.selectbox(
                "Situação da Infra-estrutura p/ Visita Técnica",
                SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                key="new_sit_infra"
            )
            data_visita = st.date_input("Data da Visita Técnica (opcional)", value=None, key="new_data_visita")
            parecer_visita = st.selectbox(
                "Parecer da Visita Técnica",
                SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                key="new_parecer_visita"
            )
            adequacoes_realizadas = st.text_input(
                "Adequações Após Visita Técnica Realizadas",
                value="",
                key="new_adequacoes"
            )
            data_finalizacao = st.date_input(
                "Data de Finalização das Adequações (opcional)",
                value=None,
                key="new_data_finalizacao"
            )
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': sit_infra,
                        'DATA DA VISITA TÉCNICA': data_visita.strftime('%d/%m/%Y') if data_visita else '',
                        'PARECER DA VISITA TÉCNICA': parecer_visita,
                        'ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS': adequacoes_realizadas,
                        'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES': data_finalizacao.strftime('%d/%m/%Y') if data_finalizacao else ''
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Ag. Visita', file_path):
                        st.cache_data.clear()
                        st.success("Registro adicionado!")
                        st.rerun()
                else:
                    st.error("Cidade é obrigatória.")
        
        with st.expander("Editar ou Apagar Registro"):
            if not df.empty:
                idx = st.selectbox("Selecione uma linha", df.index, key="edit_idx")
                row = df.loc[idx]
                
                with st.expander("Editar Registro"):
                    cidade_edit = st.text_input("Cidade", value=row['CIDADE'], key="edit_cidade")
                    sit_infra_edit = st.selectbox(
                        "Situação da Infra-estrutura p/ Visita Técnica",
                        SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                        index=SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'].index(row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']) if row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] in SHEET_CONFIG['Ag. Visita']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'] else 0,
                        key="edit_sit_infra"
                    )
                    data_visita_edit = st.date_input(
                        "Data da Visita Técnica (opcional)",
                        value=pd.to_datetime(row['DATA DA VISITA TÉCNICA'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA VISITA TÉCNICA']) and row['DATA DA VISITA TÉCNICA'] else None,
                        key="edit_data_visita"
                    )
                    parecer_visita_edit = st.selectbox(
                        "Parecer da Visita Técnica",
                        SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                        index=SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'].index(row['PARECER DA VISITA TÉCNICA']) if row['PARECER DA VISITA TÉCNICA'] in SHEET_CONFIG['Ag. Visita']['columns']['PARECER DA VISITA TÉCNICA']['values'] else 0,
                        key="edit_parecer_visita"
                    )
                    adequacoes_realizadas_edit = st.text_input(
                        "Adequações Após Visita Técnica Realizadas",
                        value=row['ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS'],
                        key="edit_adequacoes"
                    )
                    data_finalizacao_edit = st.date_input(
                        "Data de Finalização das Adequações (opcional)",
                        value=pd.to_datetime(row['DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES']) and row['DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'] else None,
                        key="edit_data_finalizacao"
                    )
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = sit_infra_edit
                            df.at[idx, 'DATA DA VISITA TÉCNICA'] = data_visita_edit.strftime('%d/%m/%Y') if data_visita_edit else ''
                            df.at[idx, 'PARECER DA VISITA TÉCNICA'] = parecer_visita_edit
                            df.at[idx, 'ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS'] = adequacoes_realizadas_edit
                            df.at[idx, 'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES'] = data_finalizacao_edit.strftime('%d/%m/%Y') if data_finalizacao_edit else ''
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
    
    with tab2:
        st.markdown("### Dashboard de Aguardando Visita Técnica")
        
        limite_cidades = st.selectbox(
            "Limitar número de cidades no dashboard",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades"
        )
        
        figs = generate_ag_visita_dashboards(df, limite_cidades)
        for fig in figs:
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    render_ag_visita()