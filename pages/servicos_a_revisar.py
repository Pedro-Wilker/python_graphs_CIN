import streamlit as st
import pandas as pd
import datetime
import os
import re

ARQUIVO = os.path.join(os.path.dirname(__file__), '..', 'revisarservicos.txt')

def parse_data_linha(linha):
    partes = [p.strip() for p in linha.split('|')]
    if len(partes) < 4:
        return None
    # Ajuste da data
    data_raw = partes[3]
    match = re.match(r'(\d{1,2}) de (\w+) de (\d{4}) às (\d{2}:\d{2})', data_raw)
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
        data_formatada = data_raw
    return {
        'SERVIÇO': partes[0],
        'ORGAO': partes[1],
        'TEMPO': int(re.findall(r'\d+', partes[2])[0]) if re.findall(r'\d+', partes[2]) else 0,
        'DATA ULTIMA PUBLICACAO': data_formatada
    }

def carregar_dados():
    with open(ARQUIVO, encoding='utf-8') as f:
        linhas = f.readlines()
    dados = []
    for linha in linhas[1:]:
        if linha.strip():
            item = parse_data_linha(linha)
            if item:
                dados.append(item)
    return pd.DataFrame(dados)

def salvar_dados(df):
    with open(ARQUIVO, 'w', encoding='utf-8') as f:
        f.write('SERVIÇO | ORGAO | TEMPO | DATA ULTIMA PUBLICACAO\n')
        for _, row in df.iterrows():
            f.write(f"{row['SERVIÇO']} | {row['ORGAO']} | {row['TEMPO']} | {row['DATA ULTIMA PUBLICACAO']}\n")

def atualizar_tempo(df):
    hoje = datetime.datetime.now()
    for idx, row in df.iterrows():
        data_str = row['DATA ULTIMA PUBLICACAO']
        try:
            data_dt = datetime.datetime.strptime(data_str, "%d/%m/%Y %H:%M")
            dias = (hoje.date() - data_dt.date()).days
            df.at[idx, 'TEMPO'] = dias
        except Exception:
            pass
    return df

def main():
    st.title("Serviços a Revisar")

    df = carregar_dados()
    df = atualizar_tempo(df)

    st.dataframe(df, use_container_width=True)

    with st.expander("Adicionar novo serviço"):
        servico = st.text_input("Serviço")
        orgao = st.text_input("Órgão")
        data_pub = st.date_input("Data última publicação", datetime.date.today())
        hora_pub = st.time_input("Hora última publicação", datetime.datetime.now().time())
        if st.button("Adicionar"):
            nova_data = f"{data_pub.strftime('%d/%m/%Y')} {hora_pub.strftime('%H:%M')}"
            novo = {'SERVIÇO': servico, 'ORGAO': orgao, 'TEMPO': 0, 'DATA ULTIMA PUBLICACAO': nova_data}
            df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
            salvar_dados(df)
            st.success("Serviço adicionado!")

    st.write("Selecione uma linha para editar ou apagar:")

    if not df.empty:
        idx = st.selectbox("Linha", df.index)
        if st.button("Apagar"):
            df = df.drop(idx).reset_index(drop=True)
            salvar_dados(df)
            st.success("Serviço removido!")
        with st.expander("Editar linha selecionada"):
            servico_edit = st.text_input("Serviço", value=df.at[idx, 'SERVIÇO'])
            orgao_edit = st.text_input("Órgão", value=df.at[idx, 'ORGAO'])
            data_edit = st.text_input("Data última publicação", value=df.at[idx, 'DATA ULTIMA PUBLICACAO'])
            if st.button("Salvar edição"):
                df.at[idx, 'SERVIÇO'] = servico_edit
                df.at[idx, 'ORGAO'] = orgao_edit
                df.at[idx, 'DATA ULTIMA PUBLICACAO'] = data_edit
                salvar_dados(df)
                st.success("Serviço atualizado!")