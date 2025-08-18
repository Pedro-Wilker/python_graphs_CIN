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
    try:
        with open(ARQUIVO, encoding='utf-8') as f:
            linhas = f.readlines()
        dados = []
        for linha in linhas[1:]:
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
        try:
            data_dt = datetime.datetime.strptime(data_str, "%d/%m/%Y %H:%M")
            dias = (hoje.date() - data_dt.date()).days
            df.at[idx, 'TEMPO'] = dias
        except Exception:
            pass
    return df

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
    
    st.markdown("### Dados de Serviços a Revisar")
    st.dataframe(df, use_container_width=True)