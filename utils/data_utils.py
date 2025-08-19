import pandas as pd
import re
from datetime import datetime
import numpy as np
import streamlit as st
import os
import openpyxl
from openpyxl.utils.dataframe import dataframe_to_rows
from io import BytesIO

# Caminho padrão do arquivo Excel (relativo ao diretório do projeto)
EXCEL_FILE = os.path.join(os.path.dirname(__file__), "..", "ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx")

# Caminho alternativo para depuração
FALLBACK_EXCEL_FILE = r"C:/Users/re049227/Documents/python_graphs_CIN/ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"

# Definição dos tipos de dados esperados para cada aba (SHEET_CONFIG remains unchanged)
SHEET_CONFIG = {
    # ... (keeping your existing SHEET_CONFIG as provided)
}

@st.cache_data
def load_excel(sheet_name, _file_path=EXCEL_FILE):
    """Carrega uma aba específica do arquivo Excel com caching."""
    try:
        file_path = _file_path
        if isinstance(file_path, str) and not os.path.exists(file_path):
            st.warning(f"Arquivo não encontrado no caminho principal: {os.path.abspath(file_path)}")
            file_path = FALLBACK_EXCEL_FILE
            if not os.path.exists(file_path):
                st.error(f"Arquivo não encontrado no caminho alternativo: {os.path.abspath(file_path)}")
                st.markdown("""
                ### Possíveis Soluções
                - Verifique se o arquivo `ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx` está em `C:\\Users\\re049227\\Documents\\python_graphs_CIN\\`.
                - Confirme se o nome do arquivo está correto (sem espaços extras ou caracteres ocultos).
                - Se o arquivo foi carregado via upload, certifique-se de que o módulo `upload_excel.py` está configurado corretamente.
                - Em produção, verifique o caminho do arquivo no servidor ou contêiner.
                """)
                return pd.DataFrame()
        
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        df.columns = df.columns.str.replace('PREFEITURA DE', 'PREFEITURAS DE', regex=False)
        
        expected_cols = list(SHEET_CONFIG.get(sheet_name, {}).get('columns', {}).keys())
        missing_cols = [col for col in expected_cols if col not in df.columns]
        if missing_cols:
            for col in missing_cols:
                col_type = SHEET_CONFIG.get(sheet_name, {}).get('columns', {}).get(col, {}).get('type', 'string')
                if col_type in ['date', 'datetime', 'training_period']:
                    df[col] = pd.NaT
                elif col_type in ['boolean']:
                    df[col] = False
                elif col_type in ['int', 'float']:
                    df[col] = 0
                else:
                    df[col] = ''
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x).replace('\n', ' ').strip() if pd.notnull(x) else '')
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar a aba {sheet_name}: {str(e)}")
        return pd.DataFrame()

def parse_training_period(period):
    """Parseia o período de treinamento em formatos variados e retorna as datas de início e fim."""
    if pd.isna(period) or period in ['-', '', 'VAZIO', 'N-PREV.', 'nan']:
        return pd.Series([pd.NaT, pd.NaT])
    
    try:
        period = str(period).strip()
        if not period or period in ['-', 'VAZIO', 'N-PREV.']:
            return pd.Series([pd.NaT, pd.NaT])
        
        parts = re.split(r'\s*(?:à|a)\s*', period, flags=re.IGNORECASE)
        if len(parts) != 2:
            return pd.Series([pd.NaT, pd.NaT])
        
        start_date, end_date = parts
        for date in [start_date, end_date]:
            parts = date.split('/')
            if len(parts) == 2:
                date = f"{date}/2025"
        
        for fmt in ['%d/%m/%Y', '%d/%m/%y']:
            try:
                start_dt = pd.to_datetime(start_date, format=fmt, errors='coerce')
                end_dt = pd.to_datetime(end_date, format=fmt, errors='coerce')
                if pd.notna(start_dt) and pd.notna(end_dt):
                    return pd.Series([start_dt, end_dt])
            except:
                continue
        
        return pd.Series([pd.NaT, pd.NaT])
    except Exception:
        return pd.Series([pd.NaT, pd.NaT])

def clean_phone_number(phone):
    """Limpa e padroniza números de telefone."""
    if pd.isna(phone) or phone in ['-', 'sn', 'vazio', 'VAZIO', 'nan']:
        return ''
    phone = str(phone).strip()
    phone = re.sub(r'[^\d]', '', phone)
    if len(phone) >= 10:
        return f"({phone[:2]}) {phone[2:7]}-{phone[7:]}"
    return ''

def clean_email(email):
    """Limpa e padroniza e-mails."""
    if pd.isna(email) or email in ['-', 'sn', 'vazio', 'VAZIO', 'nan']:
        return ''
    email = str(email).strip().lower()
    if re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
        return email
    return ''

def clean_time(time):
    """Limpa e padroniza horários."""
    if pd.isna(time) or time in ['-', 'sn', 'vazio', 'VAZIO', 'nan']:
        return ''
    time = str(time).strip()
    try:
        pd.to_datetime(time, format='%H:%M:%S')
        return time
    except:
        try:
            pd.to_datetime(time, format='%H:%M')
            return time + ':00'
        except:
            return ''

@st.cache_data
def process_sheet_data(df, sheet_name):
    """Processa os dados de uma aba com base na configuração definida."""
    if sheet_name not in SHEET_CONFIG:
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].dt.strftime('%d/%m/%Y %H:%M:%S')
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '').replace('nan', '').str.replace('\n', ' ', regex=False).str.strip()
        return df
    
    config = SHEET_CONFIG[sheet_name]['columns']
    for col, col_config in config.items():
        if col not in df.columns:
            col_type = col_config['type']
            if col_type in ['date', 'datetime', 'training_period']:
                df[col] = pd.NaT
            elif col_type in ['boolean']:
                df[col] = False
            elif col_type in ['int', 'float']:
                df[col] = 0
            else:
                df[col] = ''
            continue
        
        col_type = col_config['type']
        if col_type == 'string':
            df[col] = df[col].astype(str).replace('nan', '').str.replace('\n', ' ', regex=False).str.strip()
        elif col_type == 'categorical':
            allowed_values = col_config.get('values', [])
            df[col] = df[col].apply(lambda x: x if pd.notnull(x) and str(x).strip() in allowed_values else '')
        elif col_type == 'date':
            df[col] = pd.to_datetime(df[col], format=col_config.get('format', '%d/%m/%Y'), errors='coerce')
            df[col] = df[col].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notna(x) else '')
        elif col_type == 'datetime':
            df[col] = pd.to_datetime(df[col], format=col_config.get('format', '%d/%m/%Y %H:%M'), errors='coerce')
            df[col] = df[col].apply(lambda x: x.strftime('%d/%m/%Y %H:%M') if pd.notna(x) else '')
        elif col_type == 'boolean':
            df[col] = df[col].apply(lambda x: True if str(x).strip().upper() in ['X', 'SIM', 'TRUE'] else False)
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
    
    return df

@st.cache_data
def process_excel_file(uploaded_file=None):
    """Processa todas as abas do arquivo Excel e retorna um dicionário de DataFrames."""
    processed_data = {}
    file_path = EXCEL_FILE
    
    if uploaded_file is not None:
        st.write(f"[DEBUG] Usando arquivo carregado via upload: {uploaded_file.name}")
        file_path = uploaded_file
    
    try:
        if isinstance(file_path, str) and not os.path.exists(file_path):
            st.warning(f"Arquivo não encontrado no caminho principal: {os.path.abspath(file_path)}")
            file_path = FALLBACK_EXCEL_FILE
            if not os.path.exists(file_path):
                st.error(f"Arquivo não encontrado no caminho alternativo: {os.path.abspath(file_path)}")
                return processed_data
        
        xls = pd.ExcelFile(file_path, engine='openpyxl')
        for sheet_name in SHEET_CONFIG.keys():
            if sheet_name not in xls.sheet_names:
                st.warning(f"Aba '{sheet_name}' não encontrada no arquivo Excel.")
                processed_data[sheet_name] = pd.DataFrame()
                continue
            try:
                df = load_excel(sheet_name, file_path)
                processed_data[sheet_name] = process_sheet_data(df, sheet_name)
            except Exception as e:
                st.warning(f"Erro ao processar a aba {sheet_name}: {str(e)}")
                processed_data[sheet_name] = pd.DataFrame()
    except Exception as e:
        st.error(f"Erro ao abrir o arquivo Excel: {str(e)}")
    return processed_data

def save_excel(df, sheet_name, file_path=EXCEL_FILE):
    """Salva um DataFrame em uma aba específica do arquivo Excel."""
    try:
        # Verificar se o arquivo existe
        if isinstance(file_path, str) and not os.path.exists(file_path):
            st.warning(f"Arquivo não encontrado no caminho principal: {os.path.abspath(file_path)}")
            file_path = FALLBACK_EXCEL_FILE
            if not os.path.exists(file_path):
                # Criar um novo arquivo Excel se não existir
                wb = openpyxl.Workbook()
                wb.save(file_path)
        
        # Carregar o workbook
        wb = openpyxl.load_workbook(file_path) if isinstance(file_path, str) else openpyxl.load_workbook(file_path)
        
        # Verificar se a aba existe, senão criar
        if sheet_name not in wb.sheetnames:
            wb.create_sheet(sheet_name)
        
        # Selecionar a aba
        ws = wb[sheet_name]
        
        # Limpar a aba existente
        ws.delete_rows(1, ws.max_row)
        
        # Adicionar cabeçalhos
        headers = df.columns.tolist()
        ws.append(headers)
        
        # Adicionar dados
        for row in dataframe_to_rows(df, index=False, header=False):
            ws.append([str(cell).replace('NaT', '') if pd.notna(cell) else '' for cell in row])
        
        # Ajustar largura das colunas
        for col in range(1, len(df.columns) + 1):
            ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20
        
        # Salvar o arquivo
        if isinstance(file_path, str):
            wb.save(file_path)
        else:
            output = BytesIO()
            wb.save(output)
            file_path.seek(0)
            file_path.write(output.getvalue())
        
        st.success(f"Dados salvos com sucesso na aba '{sheet_name}'!")
        return True
    except Exception as e:
        st.error(f"Erro ao salvar a aba {sheet_name}: {str(e)}")
        return False