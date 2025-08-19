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
import plotly.graph_objects as go

ARQUIVO = os.path.join(os.path.dirname(__file__), '..', 'revisarservicos.txt')

def parse_data_linha(linha):
    try:
        # Ignorar a linha de cabeçalho
        if linha.strip().lower().startswith('serviço | orgao | tempo | data ultima publicacao'):
            return None

        partes = [p.strip() for p in linha.split('|')]
        # Inicializar valores padrão
        servico = ''
        orgao = ''
        tempo = 0
        data_formatada = ''

        # Atribuir valores com base no número de partes
        if len(partes) >= 1:
            servico = partes[0] if partes[0] else ''
        if len(partes) >= 2:
            segundo_campo = partes[1]
            match_tempo = re.search(r'(\d+)$', segundo_campo)
            if match_tempo:
                tempo = int(match_tempo.group(1))
                orgao = segundo_campo[:match_tempo.start()].strip()
            else:
                orgao = segundo_campo
                tempo = 0
        if len(partes) >= 3:
            try:
                tempo = int(re.findall(r'\d+', partes[2])[0]) if re.findall(r'\d+', partes[2]) else tempo
            except (ValueError, IndexError):
                pass
        if len(partes) >= 4 and partes[3]:
            data_raw = partes[3]
            # Tentar o formato principal: "dd de mês de aaaa" com horário opcional
            match = re.match(r'(\d{1,2})\s*de\s*(\w+)\s*(?:de\s*)?(\d{4})(?:\s*às\s*(\d{2}:\d{2}))?', data_raw, re.IGNORECASE)
            if match:
                groups = match.groups()
                dia = groups[0]
                mes = groups[1]
                ano = groups[2]
                hora = groups[3] if len(groups) > 3 else None
                meses = {
                    'january': '01', 'february': '02', 'march': '03', 'april': '04',
                    'may': '05', 'june': '06', 'july': '07', 'august': '08',
                    'september': '09', 'october': '10', 'november': '11', 'december': '12',
                    'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04',
                    'maio': '05', 'junho': '06', 'julho': '07', 'agosto': '08',
                    'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'
                }
                mes_num = meses.get(mes.lower(), '01')
                data_formatada = f"{dia.zfill(2)}/{mes_num}/{ano}" + (f" {hora}" if hora else "")
            else:
                # Fallback para outros formatos
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y', '%Y-%m-%d']:
                    try:
                        data_dt = pd.to_datetime(data_raw, format=fmt, errors='coerce')
                        if pd.notna(data_dt):
                            data_formatada = data_dt.strftime('%d/%m/%Y')
                            break
                    except:
                        continue
                else:
                    st.warning(f"Formato de data inválido na linha: {linha}")
                    data_formatada = ''

        return {
            'SERVIÇO': servico,
            'ORGAO': orgao,
            'TEMPO': tempo,
            'DATA ULTIMA PUBLICACAO': data_formatada
        }
    except Exception as e:
        st.error(f"Erro ao processar linha: {linha}. Detalhes: {str(e)}")
        return None

def carregar_dados():
    try:
        with open(ARQUIVO, encoding='utf-8') as f:
            linhas = f.readlines()
        dados = []
        for linha in linhas:
            if linha.strip():
                item = parse_data_linha(linha)
                if item:
                    dados.append(item)
        df = pd.DataFrame(dados)
        if df.empty:
            st.warning("Nenhum dado válido encontrado no arquivo revisarservicos.txt.")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo revisarservicos.txt: {str(e)}")
        return pd.DataFrame()

def atualizar_tempo(df):
    hoje = datetime.datetime.now()
    for idx, row in df.iterrows():
        data_str = row['DATA ULTIMA PUBLICACAO']
        if data_str and data_str.strip():
            try:
                for fmt in ['%d/%m/%Y %H:%M', '%d/%m/%Y']:
                    try:
                        data_dt = datetime.datetime.strptime(data_str, fmt)
                        dias = (hoje.date() - data_dt.date()).days
                        df.at[idx, 'TEMPO'] = dias
                        break
                    except ValueError:
                        continue
                else:
                    df.at[idx, 'TEMPO'] = 0
                    st.warning(f"Data inválida na linha {idx}: {data_str}")
            except Exception as e:
                df.at[idx, 'TEMPO'] = 0
                st.warning(f"Erro ao processar data na linha {idx}: {data_str}. Detalhes: {str(e)}")
        else:
            df.at[idx, 'TEMPO'] = 0
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
        - Exemplo de linha válida: 'Serviço A | Cidade X | 150 | 15 de Janeiro de 2025 às 10:00'
        """)
        return
    
    df = atualizar_tempo(df)

    # Aba de navegação: Dados e Dashboard
    tab1, tab2 = st.tabs(["Dados", "Dashboard"])

    with tab1:
        st.markdown("### Dados de Serviços a Revisar")
        limite_listagem = st.selectbox("Limitar número de serviços na listagem", [2, 5, 10, 15, 20, 50, 100, "Sem Limites"], index=7, key="limit_list")
        df_display = df.head(limite_listagem) if limite_listagem != "Sem Limites" else df
        st.dataframe(df_display, use_container_width=True)

        excel_data = to_excel(df_display)
        st.download_button(
            label="Exportar como Excel",
            data=excel_data,
            file_name="servicos_a_revisar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

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
                    data_edit = st.date_input(
                        "Data Última Publicação (opcional)",
                        value=pd.to_datetime(row['DATA ULTIMA PUBLICACAO'], errors='coerce').date() if pd.notna(row['DATA ULTIMA PUBLICACAO']) else None,
                        key="edit_data"
                    )
                    hora_edit = st.time_input(
                        "Hora Última Publicação (opcional)",
                        value=pd.to_datetime(row['DATA ULTIMA PUBLICACAO'], errors='coerce').time() if pd.notna(row['DATA ULTIMA PUBLICACAO']) and ' ' in row['DATA ULTIMA PUBLICACAO'] else None,
                        key="edit_hora"
                    ) if data_edit else None
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
        servico_selecionado = st.selectbox("Selecione um Serviço (opcional)", ["Nenhum"] + df['SERVIÇO'].tolist(), key="servico_select")
        limite_grafico = st.selectbox("Limitar número de serviços nos gráficos", [2, 5, 10, 15, 20, 50, 100, "Sem Limites"], index=7, key="limit_graph")
        df_grafico = df.head(limite_grafico) if limite_grafico != "Sem Limites" else df
        df_grafico['TEMPO'] = pd.to_numeric(df_grafico['TEMPO'], errors='coerce').fillna(0).astype(int)
        if not df_grafico.empty:
            df_valid = df_grafico[df_grafico['TEMPO'] > 0]
            if not df_valid.empty:
                df_max_min = df_valid.loc[[df_valid['TEMPO'].idxmax(), df_valid['TEMPO'].idxmin()]]
            else:
                df_max_min = df_grafico.head(2)
                st.warning("Nenhum serviço com TEMPO maior que 0. Mostrando os primeiros registros disponíveis.")
            if servico_selecionado != "Nenhum":
                if servico_selecionado not in df_max_min['SERVIÇO'].values:
                    df_servico = df_grafico[df_grafico['SERVIÇO'] == servico_selecionado]
                    if not df_servico.empty:
                        df_max_min = pd.concat([df_max_min, df_servico], ignore_index=True)
            df_max_min = df_max_min.reset_index()
            df_max_min['ÍNDICE'] = df_max_min.index + 1
            fig_max_min = px.line(
                df_max_min,
                x='ÍNDICE',
                y='TEMPO',
                color='SERVIÇO',
                title='Serviços com Maior e Menor Tempo desde Última Publicação' + (f' (Comparado com {servico_selecionado})' if servico_selecionado != "Nenhum" else ''),
                labels={'ÍNDICE': 'Serviço', 'TEMPO': 'Dias'},
                height=400,
                markers=True,
                text='TEMPO'
            )
            fig_max_min.update_traces(
                line=dict(width=2),
                marker=dict(size=10),
                textposition='top center',
                hovertemplate='Serviço: %{customdata}<br>Dias: %{y}<extra></extra>',
                customdata=df_max_min['SERVIÇO']
            )
            fig_max_min.update_xaxes(tickvals=df_max_min['ÍNDICE'], ticktext=df_max_min['ÍNDICE'])
            st.plotly_chart(fig_max_min, use_container_width=True)
        else:
            st.warning("Nenhum dado disponível para o gráfico de maior e menor tempo.")
        df_acima_120 = df_grafico[df_grafico['TEMPO'] > 120]
        if not df_acima_120.empty:
            df_acima_120 = df_acima_120.reset_index()
            df_acima_120['ÍNDICE'] = df_acima_120.index + 1
            fig_acima_120 = px.line(
                df_acima_120.sort_values('TEMPO', ascending=False),
                x='ÍNDICE',
                y='TEMPO',
                color='SERVIÇO',
                title='Serviços com Mais de 120 Dias desde Última Publicação',
                labels={'ÍNDICE': 'Serviço', 'TEMPO': 'Dias'},
                height=400,
                markers=True,
                text='TEMPO'
            )
            fig_acima_120.update_traces(
                line=dict(width=2),
                marker=dict(size=10),
                textposition='top center',
                hovertemplate='Serviço: %{customdata}<br>Dias: %{y}<extra></extra>',
                customdata=df_acima_120['SERVIÇO']
            )
            fig_acima_120.update_xaxes(tickvals=df_acima_120['ÍNDICE'], ticktext=df_acima_120['ÍNDICE'])
            st.plotly_chart(fig_acima_120, use_container_width=True)
        else:
            st.warning("Nenhum serviço com mais de 120 dias desde a última publicação.")