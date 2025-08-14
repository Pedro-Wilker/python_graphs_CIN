import pandas as pd
import re
from datetime import datetime
import numpy as np

EXCEL_FILE = "ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"

def load_excel(sheet_name):
    """Carrega uma aba do arquivo Excel e normaliza os nomes das colunas."""
    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine='openpyxl')
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        return df
    except Exception as e:
        raise Exception(f"Erro ao carregar a aba {sheet_name}: {str(e)}")

def parse_training_period(period):
    """Trata períodos de treinamento no formato 'DD/MM a DD/MM/YY'."""
    if pd.isna(period) or not isinstance(period, str) or period.strip() == '' or period.strip().upper() in ['N-PREV.', '-']:
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