import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_utils import load_excel, process_sheet_data, save_excel, SHEET_CONFIG, EXCEL_FILE
import plotly.express as px
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows

@st.cache_data
def load_and_process_ag_instalacao(_file_path=EXCEL_FILE):
    """Carrega e processa a aba Ag_Instalacao com caching."""
    try:
        raw_df = load_excel('Ag_Instalacao', _file_path)
        if raw_df.empty:
            st.error("Nenhum dado disponível para a aba 'Ag_Instalacao'. Verifique o nome da aba no arquivo Excel.")
            return pd.DataFrame()
        
        # Verificar colunas esperadas
        expected_columns = list(SHEET_CONFIG['Ag_Instalacao']['columns'].keys())
        missing_columns = [col for col in expected_columns if col not in raw_df.columns]
        if missing_columns:
            for col in missing_columns:
                col_type = SHEET_CONFIG['Ag_Instalacao']['columns'][col].get('type', 'string')
                if col_type == 'date':
                    raw_df[col] = pd.NaT
                elif col_type == 'categorical':
                    raw_df[col] = ''
                elif col_type == 'boolean':
                    raw_df[col] = False
                else:
                    raw_df[col] = ''
        
        df = process_sheet_data(raw_df, 'Ag_Instalacao')
        return df
    except Exception as e:
        st.error(f"Erro ao processar a aba Ag_Instalacao: {str(e)}")
        return pd.DataFrame()

def to_excel(df):
    """Converte DataFrame para Excel com estilização."""
    output = BytesIO()
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Relatório de Datas'

    headers = df.columns.tolist()
    for col, header in enumerate(headers, 1):
        cell = worksheet.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")

    for row in dataframe_to_rows(df, index=False, header=False):
        worksheet.append(row)

    for col in range(1, len(df.columns) + 1):
        worksheet.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

    workbook.save(output)
    return output.getvalue()

def render_ag_instalacao(uploaded_file=None):
    st.markdown("""
        <h3>Aguardando Instalação <span class="material-icons" style="vertical-align: middle; color: #004aad;">construction</span></h3>
    """, unsafe_allow_html=True)
    
    file_path = uploaded_file if uploaded_file else EXCEL_FILE
    df = load_and_process_ag_instalacao(file_path)
    
    if df.empty:
        st.error("Nenhum dado disponível para a aba 'Ag_Instalacao'. Verifique o arquivo Excel e o nome da aba.")
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
                SHEET_CONFIG['Ag_Instalacao']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                key="new_sit_infra"
            )
            parecer_visita = st.selectbox(
                "Parecer da Visita Técnica",
                SHEET_CONFIG['Ag_Instalacao']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                key="new_parecer_visita"
            )
            realizou_treinamento = st.checkbox("Realizou Treinamento?", key="new_realizou_treinamento")
            situacao_termo = st.selectbox(
                "Situação do Novo Termo de Cooperação",
                SHEET_CONFIG['Ag_Instalacao']['columns']['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO']['values'],
                key="new_situacao_termo"
            )
            data_do = st.date_input("Data do D.O. (opcional)", value=None, key="new_data_do")
            apto_instalacao = st.checkbox("Apto para Instalação?", key="new_apto_instalacao")
            data_instalacao = st.date_input("Data da Instalação (opcional)", value=None, key="new_data_instalacao")
            data_inicio_atend = st.date_input("Data do Início Atend. (opcional)", value=None, key="new_data_inicio_atend")
            
            if st.button("Adicionar Registro", key="add_button"):
                if cidade:
                    novo = {
                        'CIDADE': cidade,
                        'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': sit_infra,
                        'PARECER DA VISITA TÉCNICA': parecer_visita,
                        'REALIZOU TREINAMENTO?': realizou_treinamento,
                        'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': situacao_termo,
                        'DATA DO D.O.': data_do.strftime('%d/%m/%Y') if data_do else '',
                        'APTO PARA INSTALAÇÃO': apto_instalacao,
                        'DATA DA INSTALAÇÃO': data_instalacao.strftime('%d/%m/%Y') if data_instalacao else '',
                        'DATA DO INÍCIO ATEND.': data_inicio_atend.strftime('%d/%m/%Y') if data_inicio_atend else ''
                    }
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    if save_excel(df, 'Ag_Instalacao', file_path):
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
                    sit_infra_edit = st.selectbox(
                        "Situação da Infra-estrutura p/ Visita Técnica",
                        SHEET_CONFIG['Ag_Instalacao']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'],
                        index=SHEET_CONFIG['Ag_Instalacao']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'].index(row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']) if row['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] in SHEET_CONFIG['Ag_Instalacao']['columns']['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA']['values'] else 0,
                        key="edit_sit_infra"
                    )
                    parecer_visita_edit = st.selectbox(
                        "Parecer da Visita Técnica",
                        SHEET_CONFIG['Ag_Instalacao']['columns']['PARECER DA VISITA TÉCNICA']['values'],
                        index=SHEET_CONFIG['Ag_Instalacao']['columns']['PARECER DA VISITA TÉCNICA']['values'].index(row['PARECER DA VISITA TÉCNICA']) if row['PARECER DA VISITA TÉCNICA'] in SHEET_CONFIG['Ag_Instalacao']['columns']['PARECER DA VISITA TÉCNICA']['values'] else 0,
                        key="edit_parecer_visita"
                    )
                    realizou_treinamento_edit = st.checkbox(
                        "Realizou Treinamento?",
                        value=row['REALIZOU TREINAMENTO?'],
                        key="edit_realizou_treinamento"
                    )
                    situacao_termo_edit = st.selectbox(
                        "Situação do Novo Termo de Cooperação",
                        SHEET_CONFIG['Ag_Instalacao']['columns']['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO']['values'],
                        index=SHEET_CONFIG['Ag_Instalacao']['columns']['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO']['values'].index(row['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO']) if row['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO'] in SHEET_CONFIG['Ag_Instalacao']['columns']['SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO']['values'] else 0,
                        key="edit_situacao_termo"
                    )
                    data_do_edit = st.date_input(
                        "Data do D.O. (opcional)",
                        value=pd.to_datetime(row['DATA DO D.O.'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DO D.O.']) and row['DATA DO D.O.'] else None,
                        key="edit_data_do"
                    )
                    apto_instalacao_edit = st.checkbox(
                        "Apto para Instalação?",
                        value=row['APTO PARA INSTALAÇÃO'],
                        key="edit_apto_instalacao"
                    )
                    data_instalacao_edit = st.date_input(
                        "Data da Instalação (opcional)",
                        value=pd.to_datetime(row['DATA DA INSTALAÇÃO'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DA INSTALAÇÃO']) and row['DATA DA INSTALAÇÃO'] else None,
                        key="edit_data_instalacao"
                    )
                    data_inicio_atend_edit = st.date_input(
                        "Data do Início Atend. (opcional)",
                        value=pd.to_datetime(row['DATA DO INÍCIO ATEND.'], format='%d/%m/%Y', errors='coerce').date() if pd.notna(row['DATA DO INÍCIO ATEND.']) and row['DATA DO INÍCIO ATEND.'] else None,
                        key="edit_data_inicio_atend"
                    )
                    
                    if st.button("Salvar Edição", key="save_button"):
                        if cidade_edit:
                            df.at[idx, 'CIDADE'] = cidade_edit
                            df.at[idx, 'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = sit_infra_edit
                            df.at[idx, 'PARECER DA VISITA TÉCNICA'] = parecer_visita_edit
                            df.at[idx, 'REALIZOU TREINAMENTO?'] = realizou_treinamento_edit
                            df.at[idx, 'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO'] = situacao_termo_edit
                            df.at[idx, 'DATA DO D.O.'] = data_do_edit.strftime('%d/%m/%Y') if data_do_edit else ''
                            df.at[idx, 'APTO PARA INSTALAÇÃO'] = apto_instalacao_edit
                            df.at[idx, 'DATA DA INSTALAÇÃO'] = data_instalacao_edit.strftime('%d/%m/%Y') if data_instalacao_edit else ''
                            df.at[idx, 'DATA DO INÍCIO ATEND.'] = data_inicio_atend_edit.strftime('%d/%m/%Y') if data_inicio_atend_edit else ''
                            if save_excel(df, 'Ag_Instalacao', file_path):
                                st.cache_data.clear()
                                st.success("Registro atualizado!")
                                st.rerun()
                        else:
                            st.error("Cidade é obrigatória.")
                
                with st.expander("Apagar Registro"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        if save_excel(df, 'Ag_Instalacao', file_path):
                            st.cache_data.clear()
                            st.success("Registro removido!")
                            st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")
    
    with tab2:
        st.markdown("### Dashboard de Aguardando Instalação")
        
        # Seletor para limitar o número de cidades
        limite_cidades = st.selectbox(
            "Limitar número de cidades no dashboard",
            [2, 5, 10, 15, 20, 50, 100, "Sem Limites"],
            index=7,
            key="limit_cidades"
        )
        
        # Filtrar o DataFrame com base no limite
        df_grafico = df.head(limite_cidades) if limite_cidades != "Sem Limites" else df.copy()
        
        # Gráfico 1: SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA
        st.markdown("#### Distribuição de Cidades por Situação da Infra-estrutura")
        valid_categories = ["Sem pendência", "Com Pendência", "Não Informada"]
        df_grafico['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'] = df_grafico['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].apply(
            lambda x: x if x in valid_categories else "Não Informada"
        )
        df_counts_infra = df_grafico['SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA'].value_counts().reset_index()
        df_counts_infra.columns = ['Situação', 'Contagem']
        for category in valid_categories:
            if category not in df_counts_infra['Situação'].values:
                df_counts_infra = pd.concat([df_counts_infra, pd.DataFrame({'Situação': [category], 'Contagem': [0]})], ignore_index=True)
        
        if not df_counts_infra.empty and df_counts_infra['Contagem'].sum() > 0:
            fig_infra = px.pie(
                df_counts_infra,
                names='Situação',
                values='Contagem',
                title='Cidades por Situação da Infra-estrutura para Visita Técnica',
                height=400,
                color='Situação',
                color_discrete_map={
                    'Sem pendência': '#00CC96',  # Verde
                    'Com Pendência': '#EF553B',  # Vermelho
                    'Não Informada': '#636EFA'   # Azul
                }
            )
            fig_infra.update_traces(textinfo='percent+label', textposition='inside', showlegend=True)
            fig_infra.update_layout(legend_title_text='Situação', margin=dict(t=50, b=50, l=50, r=50))
            st.plotly_chart(fig_infra, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o gráfico de situação da infra-estrutura.")
        
        # Relatório de Datas
        st.markdown("#### Relatório de Datas por Cidade")
        df_relatorio = df_grafico[['CIDADE', 'DATA DO D.O.', 'DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.']].copy()
        df_relatorio['DO para Instalação (Dias)'] = 0
        df_relatorio['Instalação para Atendimento (Dias)'] = 0
        df_relatorio['DO para Atendimento (Dias)'] = 0
        
        for idx, row in df_relatorio.iterrows():
            try:
                data_do = pd.to_datetime(row['DATA DO D.O.'], format='%d/%m/%Y', errors='coerce')
                data_instalacao = pd.to_datetime(row['DATA DA INSTALAÇÃO'], format='%d/%m/%Y', errors='coerce')
                data_inicio_atend = pd.to_datetime(row['DATA DO INÍCIO ATEND.'], format='%d/%m/%Y', errors='coerce')
                
                if pd.notna(data_do) and pd.notna(data_instalacao):
                    df_relatorio.at[idx, 'DO para Instalação (Dias)'] = (data_instalacao - data_do).days
                if pd.notna(data_instalacao) and pd.notna(data_inicio_atend):
                    df_relatorio.at[idx, 'Instalação para Atendimento (Dias)'] = (data_inicio_atend - data_instalacao).days
                if pd.notna(data_do) and pd.notna(data_inicio_atend):
                    df_relatorio.at[idx, 'DO para Atendimento (Dias)'] = (data_inicio_atend - data_do).days
            except Exception as e:
                st.warning(f"Erro ao calcular tempos para a cidade {row['CIDADE']}: {str(e)}")
        
        # Estilizar o DataFrame
        def style_dataframe(df):
            return df.style.set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#4F81BD'), ('color', 'white'), ('font-weight', 'bold'), ('text-align', 'center'), ('padding', '8px')]},
                {'selector': 'td', 'props': [('border', '1px solid #ddd'), ('padding', '8px'), ('text-align', 'center')]},
                {'selector': 'tr:nth-child(even)', 'props': [('background-color', '#f2f2f2')]},
                {'selector': 'tr:hover', 'props': [('background-color', '#e0e0e0')]}
            ]).set_properties(**{'font-size': '14px'})
        
        st.dataframe(style_dataframe(df_relatorio), use_container_width=True)
        
        # Botão para exportar o relatório como Excel
        excel_data = to_excel(df_relatorio)
        st.download_button(
            label="Exportar Relatório como Excel",
            data=excel_data,
            file_name="relatorio_datas_instalacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        # Gráfico 2: PARECER DA VISITA TÉCNICA
        st.markdown("#### Distribuição de Cidades por Parecer da Visita Técnica")
        valid_parecer = SHEET_CONFIG['Ag_Instalacao']['columns']['PARECER DA VISITA TÉCNICA']['values'] + ["Não Informado"]
        df_grafico['PARECER DA VISITA TÉCNICA'] = df_grafico['PARECER DA VISITA TÉCNICA'].apply(
            lambda x: x if x in SHEET_CONFIG['Ag_Instalacao']['columns']['PARECER DA VISITA TÉCNICA']['values'] else "Não Informado"
        )
        df_counts_parecer = df_grafico['PARECER DA VISITA TÉCNICA'].value_counts().reset_index()
        df_counts_parecer.columns = ['Parecer', 'Contagem']
        for category in valid_parecer:
            if category not in df_counts_parecer['Parecer'].values:
                df_counts_parecer = pd.concat([df_counts_parecer, pd.DataFrame({'Parecer': [category], 'Contagem': [0]})], ignore_index=True)
        
        if not df_counts_parecer.empty and df_counts_parecer['Contagem'].sum() > 0:
            fig_parecer = px.pie(
                df_counts_parecer,
                names='Parecer',
                values='Contagem',
                title='Cidades por Parecer da Visita Técnica',
                height=400,
                color_discrete_sequence=px.colors.qualitative.Plotly
            )
            fig_parecer.update_traces(textinfo='percent+label', textposition='inside', showlegend=True)
            fig_parecer.update_layout(legend_title_text='Parecer', margin=dict(t=50, b=50, l=50, r=50))
            st.plotly_chart(fig_parecer, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o gráfico de parecer da visita técnica.")
        
        # Gráfico 3: REALIZOU TREINAMENTO?
        st.markdown("#### Distribuição de Cidades por Realização de Treinamento")
        df_grafico['REALIZOU TREINAMENTO?'] = df_grafico['REALIZOU TREINAMENTO?'].map({True: 'Sim', False: 'Não'})
        df_counts_treinamento = df_grafico['REALIZOU TREINAMENTO?'].value_counts().reset_index()
        df_counts_treinamento.columns = ['Treinamento', 'Contagem']
        for category in ['Sim', 'Não']:
            if category not in df_counts_treinamento['Treinamento'].values:
                df_counts_treinamento = pd.concat([df_counts_treinamento, pd.DataFrame({'Treinamento': [category], 'Contagem': [0]})], ignore_index=True)
        
        if not df_counts_treinamento.empty and df_counts_treinamento['Contagem'].sum() > 0:
            fig_treinamento = px.pie(
                df_counts_treinamento,
                names='Treinamento',
                values='Contagem',
                title='Cidades por Realização de Treinamento',
                height=400,
                color='Treinamento',
                color_discrete_map={'Sim': '#00CC96', 'Não': '#EF553B'}
            )
            fig_treinamento.update_traces(textinfo='percent+label', textposition='inside', showlegend=True)
            fig_treinamento.update_layout(legend_title_text='Treinamento', margin=dict(t=50, b=50, l=50, r=50))
            st.plotly_chart(fig_treinamento, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o gráfico de treinamento.")