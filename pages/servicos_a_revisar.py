import streamlit as st
import pandas as pd
import datetime
import os
import re
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
import plotly.express as px

ARQUIVO = os.path.join(os.path.dirname(__file__), '..', 'revisarservicos.txt')

def parse_data_linha(linha):
    partes = [p.strip() for p in linha.split('|')]
    if len(partes) < 3:  # Reduzido para 3, pois DATA ULTIMA PUBLICACAO não é obrigatória
        return None
    data_raw = partes[3] if len(partes) > 3 else ''
    match = re.match(r'(\d{1,2}) de (\w+) de (\d{4}) às (\d{2}:\d{2})', data_raw) if data_raw else None
    if match:
        dia, mes, ano, hora = match.groups()
        meses = {
            'January': '01', 'February': '02', 'March': '03', 'April': '04',
            'May': '05', 'June': '06', 'July': '07', 'August': '08',
            'September': '09', 'October': '10', 'November': '11', 'December': '12',
            'Janeiro': '01', 'Fevereiro': '02', 'Março': '03', 'Abril': '04',
            'Maio': '05', 'Junho': '06', 'Julho': '07', 'Agosto': '08',
            'Setembro': '09', 'Outubro': '10', 'Novembro': '11', 'Dezembro': '12'
        }
        mes_num = meses.get(mes, '01')
        data_formatada = f"{dia.zfill(2)}/{mes_num}/{ano} {hora}"
    else:
        data_formatada = data_raw if data_raw else ''
    return {
        'SERVIÇO': partes[0],
        'ORGAO': partes[1],
        'TEMPO': int(re.findall(r'\d+', partes[2])[0]) if re.findall(r'\d+', partes[2]) else 0,
        'DATA ULTIMA PUBLICACAO': data_formatada
    }

def carregar_dados():
    try:
        with open(ARQUIVO, encoding='utf-8') as f:
            linhas = f.readlines()
        dados = []
        for linha in linhas[1:]:  # Ignora a primeira linha (cabeçalho)
            if linha.strip():
                item = parse_data_linha(linha)
                if item:
                    dados.append(item)
        return pd.DataFrame(dados)
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo revisarservicos.txt: {str(e)}")
        return pd.DataFrame()

def atualizar_tempo(df):
    hoje = datetime.datetime.now()
    for idx, row in df.iterrows():
        data_str = row['DATA ULTIMA PUBLICACAO']
        if data_str and data_str.strip():
            try:
                data_dt = datetime.datetime.strptime(data_str, "%d/%m/%Y %H:%M")
                dias = (hoje.date() - data_dt.date()).days
                df.at[idx, 'TEMPO'] = dias
            except ValueError:
                df.at[idx, 'TEMPO'] = 0  # Mantém 0 se a data for inválida
        else:
            df.at[idx, 'TEMPO'] = 0  # Define 0 se não houver data
    return df

def salvar_dados(df):
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write('SERVIÇO | ORGAO | TEMPO | DATA ULTIMA PUBLICACAO\n')
        for _, row in df.iterrows():
            data_str = row['DATA ULTIMA PUBLICACAO'] if row['DATA ULTIMA PUBLICACAO'] else ''
            f.write(f"{row['SERVIÇO']} | {row['ORGAO']} | {row['TEMPO']} | {data_str}\n")

def to_excel(df):
    output = BytesIO()
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = 'Serviços a Revisar'

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

def render_servicos_a_revisar():
    st.markdown("""
        <h3>Serviços a Revisar <span class="material-icons" style="vertical-align: middle; color: #004aad;">checklist</span></h3>
    """, unsafe_allow_html=True)
    
    df = carregar_dados()
    if df.empty:
        st.error("Nenhum dado carregado do arquivo revisarservicos.txt.")
        st.markdown("""
        ### Possíveis Soluções
        - Verifique se o arquivo `revisarservicos.txt` está no diretório raiz do projeto.
        - Confirme se o arquivo contém dados no formato correto (ex.: SERVIÇO | ORGAO | TEMPO | DATA ULTIMA PUBLICACAO).
        """)
        return
    
    df = atualizar_tempo(df)

    # Aba de navegação: Dados e Dashboard
    tab1, tab2 = st.tabs(["Dados", "Dashboard"])

    with tab1:
        st.markdown("### Dados de Serviços a Revisar")
        # Limite para a listagem
        limite_listagem = st.selectbox("Limitar número de serviços na listagem", [2, 5, 10, 15, 20, 50, 100, "Sem Limites"], index=7, key="limit_list")
        df_display = df.head(limite_listagem) if limite_listagem != "Sem Limites" else df
        st.dataframe(df_display, use_container_width=True)

        # Botão para exportar como Excel
        excel_data = to_excel(df_display)
        st.download_button(
            label="Exportar como Excel",
            data=excel_data,
            file_name="servicos_a_revisar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # Modais para ações
        with st.expander("Adicionar Novo Serviço"):
            servico = st.text_input("Serviço", key="new_servico")
            orgao = st.text_input("Órgão", key="new_orgao")
            data_pub = st.date_input("Data Última Publicação (opcional)", value=None, key="new_data")
            hora_pub = st.time_input("Hora Última Publicação (opcional)", value=None, key="new_hora") if data_pub else None
            if st.button("Adicionar Serviço", key="add_button"):
                if servico and orgao:
                    nova_data = f"{data_pub.strftime('%d/%m/%Y') if data_pub else ''} {hora_pub.strftime('%H:%M') if hora_pub else ''}".strip() if data_pub and hora_pub else ''
                    novo = {'SERVIÇO': servico, 'ORGAO': orgao, 'TEMPO': 0, 'DATA ULTIMA PUBLICACAO': nova_data}
                    df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                    df = atualizar_tempo(df)
                    salvar_dados(df)
                    st.success("Serviço adicionado!")
                    st.rerun()
                else:
                    st.error("Serviço e Órgão são obrigatórios.")

        with st.expander("Editar ou Apagar Serviço"):
            if not df.empty:
                idx = st.selectbox("Selecione uma linha", df.index, key="edit_idx")
                row = df.loc[idx]

                with st.expander("Editar Serviço"):
                    servico_edit = st.text_input("Serviço", value=row['SERVIÇO'], key="edit_servico")
                    orgao_edit = st.text_input("Órgão", value=row['ORGAO'], key="edit_orgao")
                    data_edit = st.date_input("Data Última Publicação (opcional)", value=pd.to_datetime(row['DATA ULTIMA PUBLICACAO'], errors='coerce').date() if pd.notna(row['DATA ULTIMA PUBLICACAO']) else None, key="edit_data")
                    hora_edit = st.time_input("Hora Última Publicação (opcional)", value=pd.to_datetime(row['DATA ULTIMA PUBLICACAO'], errors='coerce').time() if pd.notna(row['DATA ULTIMA PUBLICACAO']) else None, key="edit_hora") if data_edit else None
                    if st.button("Salvar Edição", key="save_button"):
                        if servico_edit and orgao_edit:
                            nova_data = f"{data_edit.strftime('%d/%m/%Y') if data_edit else ''} {hora_edit.strftime('%H:%M') if hora_edit else ''}".strip() if data_edit and hora_edit else ''
                            df.at[idx, 'SERVIÇO'] = servico_edit
                            df.at[idx, 'ORGAO'] = orgao_edit
                            df.at[idx, 'DATA ULTIMA PUBLICACAO'] = nova_data
                            df = atualizar_tempo(df)
                            salvar_dados(df)
                            st.success("Serviço atualizado!")
                            st.rerun()
                        else:
                            st.error("Serviço e Órgão são obrigatórios.")

                with st.expander("Apagar Serviço"):
                    if st.button("Confirmar Apagar", key="delete_button"):
                        df = df.drop(idx).reset_index(drop=True)
                        salvar_dados(df)
                        st.success("Serviço removido!")
                        st.rerun()
            else:
                st.warning("Nenhuma linha disponível para editar ou apagar.")

    with tab2:
        st.markdown("### Dashboard de Serviços a Revisar")
        # Limite para os gráficos
        limite_grafico = st.selectbox("Limitar número de serviços nos gráficos", [2, 5, 10, 15, 20, 50, 100, "Sem Limites"], index=7, key="limit_graph")
        df_grafico = df.head(limite_grafico) if limite_grafico != "Sem Limites" else df

        # Garantir que todas as colunas sejam strings para evitar erros de serialização
        df_grafico = df_grafico.astype(str)

        # Gráfico de Linha
        fig_line = px.line(df_grafico.sort_values('TEMPO', ascending=False), x='SERVIÇO', y='TEMPO', title='Ranking de Serviços por Tempo desde Última Publicação',
                          labels={'SERVIÇO': 'Serviços', 'TEMPO': 'Dias'}, height=400)
        fig_line.update_traces(mode='lines+markers')
        st.plotly_chart(fig_line)

        # Gráfico de Colunas
        fig_bar = px.bar(df_grafico.sort_values('TEMPO', ascending=False), x='SERVIÇO', y='TEMPO', title='Ranking de Serviços por Tempo desde Última Publicação',
                        labels={'SERVIÇO': 'Serviços', 'TEMPO': 'Dias'}, height=400)
        st.plotly_chart(fig_bar)