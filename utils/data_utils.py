import pandas as pd
import re
from datetime import datetime
import numpy as np
import tempfile
import os

EXCEL_FILE = "ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"

# Definição dos tipos de dados esperados para cada aba (mantido igual ao anterior)
SHEET_CONFIG = {
    'Geral Amplo': {
        'sheet_name': 'Geral Amplo',
        'columns': {
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': {'type': 'categorical', 'values': ['Sem pendência', 'Com pendência', 'Não informado']},
            'DATA DA VISITA TÉCNICA': {'type': 'date', 'format': '%d/%m/%Y'},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado']},
            'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?': {'type': 'empty'},
            'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES': {'type': 'empty'},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'TURMA': {'type': 'int'},
            'REALIZOU TREINAMENTO?': {'type': 'boolean'},
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': {'type': 'string'},
            'DATA DO D.O.': {'type': 'date', 'format': '%d/%m/%Y'},
            'APTO PARA INSTALAÇÃO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA ASSINATURA': {'type': 'date', 'format': '%d/%m/%Y'}
        }
    },
    # ... (manter as configurações de todas as outras abas como no código anterior)
    'Informações': {
        'sheet_name': 'Informações',
        'columns': {
            'data/hora': {'type': 'datetime', 'format': '%d/%m/%Y %H:%M'},
            'Cidade': {'type': 'string'},
            'Nome do chefe de posto': {'type': 'string'},
            'Telefone Celular chefe de posto': {'type': 'phone'},
            'Link WhatsApp': {'type': 'string'},
            'E-mail chefe de posto': {'type': 'email'},
            'Nome do Secretário/Coordenador': {'type': 'string'},
            'Telefone do Secretário': {'type': 'phone'},
            'Link WhatsApp 2': {'type': 'string'},
            'Endereço do Posto': {'type': 'string'},
            'CEP': {'type': 'string'},
            'Ponto de referência do endereço': {'type': 'string'},
            'Telefone Fixo': {'type': 'phone', 'allow_empty': True},
            'Horário de abertura': {'type': 'time'},
            'Horário de Fechamento': {'type': 'time'},
            'E-mail da Prefeitura': {'type': 'email'},
            'Telefone da Prefeitura': {'type': 'phone', 'allow_empty': True},
            'PENDÊNCIA P/ VISITA TÉCNICA': {'type': 'string'},
            'Código do Posto': {'type': 'string'}
        }
    },
    'Chefes_Posto': {
        'sheet_name': 'Chefes_Posto',
        'columns': {
            'Cidade': {'type': 'string'},
            'Posto': {'type': 'string'},
            'Nome': {'type': 'string'},
            'E-mail': {'type': 'email'},
            'Telefone': {'type': 'phone'},
            'Turma': {'type': 'int'},
            'Data treinamento': {'type': 'training_period'},
            'Usuário': {'type': 'string'}
        }
    },
    'Produtividade': {
        'sheet_name': 'Produtividade',
        'columns': {
            'CIDADE': {'type': 'string'},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'REALIZOU TREINAMENTO': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'PREFEITURA DE': {'type': 'string'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'},
            'ABRIL': {'type': 'float'},
            'MAIO': {'type': 'float'},
            'JUNHO': {'type': 'float'},
            'JULHO': {'type': 'float'},
            'AGOSTO': {'type': 'float'},
            'SETEMBRO': {'type': 'float'},
            'OUTUBRO': {'type': 'float'},
            'NOVEMBRO': {'type': 'float'},
            'DEZEMBRO': {'type': 'float'}
        }
    }
}

def load_excel(sheet_name, file_path=EXCEL_FILE):
    """Carrega uma aba do arquivo Excel e normaliza os nomes das colunas."""
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        # Renomeia colunas 'Unnamed: X' para evitar problemas
        df.columns = [f"Coluna_{i}" if col.startswith('Unnamed:') else col for i, col in enumerate(df.columns)]
        return df
    except Exception as e:
        raise Exception(f"Erro ao carregar a aba {sheet_name} do arquivo {file_path}: {str(e)}")

def parse_training_period(period):
    """Trata períodos de treinamento no formato 'DD/MM a DD/MM/YY'."""
    if pd.isna(period) or not isinstance(period, str) or period.strip() == '' or period.strip().upper() in ['N-PREV.', '-', 'VAZIO']:
        return pd.NaT, pd.NaT
    try:
        dates = re.split(r'\s*(?:à|a)\s*', period.strip(), flags=re.IGNORECASE)
        if len(dates) != 2:
            return pd.NaT, pd.NaT
        
        start_date_str, end_date_str = dates
        start_date_str = start_date_str.strip()
        end_date_str = end_date_str.strip()
        
        if start_date_str.count('/') == 1:
            end_year = re.search(r'(\d{2})$', end_date_str)
            if end_year:
                start_date_str = f"{start_date_str}/20{end_year.group(1)}"
            else:
                start_date_str = f"{start_date_str}/2025"
        start_date = pd.to_datetime(start_date_str, format='%d/%m/%Y', errors='coerce')
        
        if end_date_str.count('/') == 1:
            end_date_str = f"{end_date_str}/2025"
        elif re.match(r'\d{2}/\d{2}/\d{2}$', end_date_str):
            end_date_str = f"{end_date_str[:6]}20{end_date_str[6:]}"
        end_date = pd.to_datetime(end_date_str, format='%d/%m/%Y', errors='coerce')
        
        return start_date, end_date
    except Exception:
        return pd.NaT, pd.NaT

def parse_date_columns(df, date_columns, date_format='%d/%m/%Y'):
    """Converte colunas de datas para datetime."""
    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
    return df

def parse_boolean_columns(df, bool_columns):
    """Converte colunas booleanas com 'X' para True e vazio para False."""
    for col in bool_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: True if str(x).strip().upper() == 'X' else False)
    return df

def clean_phone_number(value):
    """Limpa números de telefone, aceitando apenas formatos válidos."""
    if pd.isna(value) or str(value).strip() in ['', 'sn', 'não tem', '-']:
        return ''
    value = str(value).strip()
    cleaned = re.sub(r'[^\d\s-]', '', value)
    return cleaned if re.match(r'^\d{10,11}$|^\d{2}\s?\d{8,9}$|^\d{2}-\d{8,9}$', cleaned) else ''

def clean_email(value):
    """Limpa e-mails, aceitando apenas formatos válidos ou vazio."""
    if pd.isna(value) or str(value).strip() in ['', 'sn', 'não tem', '-']:
        return ''
    value = str(value).strip()
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', value):
        return value
    return ''

def clean_time(value):
    """Limpa horários, aceitando apenas formatos HH:MM:SS."""
    if pd.isna(value) or str(value).strip() in ['', 'sn', 'não tem', '-']:
        return ''
    value = str(value).strip()
    if re.match(r'^\d{2}:\d{2}:\d{2}$', value):
        return value
    return ''

def process_sheet_data(df, sheet_name):
    """Processa os dados de uma aba com base na configuração definida."""
    if sheet_name not in SHEET_CONFIG:
        # Fallback para abas não configuradas: converte todas as colunas para string
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%d/%m/%Y %H:%M:%S')
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '').replace('nan', '')
        return df
    
    config = SHEET_CONFIG[sheet_name]['columns']
    for col, col_config in config.items():
        if col not in df.columns:
            continue
        
        col_type = col_config['type']
        if col_type == 'string':
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '').replace('nan', '')
        elif col_type == 'categorical':
            allowed_values = col_config.get('values', [])
            df[col] = df[col].apply(lambda x: x if pd.notnull(x) and str(x).strip() in allowed_values else '')
        elif col_type == 'date':
            df[col] = pd.to_datetime(df[col], format=col_config.get('format', '%d/%m/%Y'), errors='coerce')
        elif col_type == 'datetime':
            df[col] = pd.to_datetime(df[col], format=col_config.get('format', '%d/%m/%Y %H:%M'), errors='coerce')
        elif col_type == 'boolean':
            df[col] = df[col].apply(lambda x: True if str(x).strip().upper() == 'X' else False)
        elif col_type == 'int':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        elif col_type == 'float':
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
        elif col_type == 'training_period':
            df[[f'{col}_INÍCIO', f'{col}_FIM']] = df[col].apply(parse_training_period).apply(pd.Series)
            df.drop(columns=[col], inplace=True)
        elif col_type == 'phone':
            df[col] = df[col].apply(clean_phone_number)
            if col_config.get('allow_empty', False):
                df[col] = df[col].replace('', np.nan)
        elif col_type == 'email':
            df[col] = df[col].apply(clean_email)
        elif col_type == 'time':
            df[col] = df[col].apply(clean_time)
        elif col_type == 'empty':
            df[col] = df[col].apply(lambda x: '' if pd.notnull(x) and str(x).strip() in ['-', 'VAZIO'] else str(x) if pd.notnull(x) else '')
    
    return df

def process_excel_file(file_path=EXCEL_FILE):
    """Processa todas as abas de um arquivo Excel com base na configuração."""
    try:
        excel_file = pd.ExcelFile(file_path)
        processed_data = {}
        
        for sheet_name in excel_file.sheet_names:
            df = load_excel(sheet_name, file_path)
            df = process_sheet_data(df, sheet_name)
            processed_data[sheet_name] = df
        
        return processed_data
    except Exception as e:
        raise Exception(f"Erro ao processar o arquivo {file_path}: {str(e)}")