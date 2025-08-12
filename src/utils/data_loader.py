import pandas as pd
import re
from datetime import datetime

def load_and_process_data(file_path):
    """
    Carrega e processa o arquivo Excel, retornando um DataFrame normalizado.
    """
    try:
        # Ler a aba 'Produtividade' do arquivo
        df = pd.read_excel(file_path, sheet_name='Produtividade', engine='openpyxl')

        # Normalizar os nomes das colunas
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        df.columns = df.columns.str.replace('PREFEITURA DE', 'PREFEITURAS DE')

        # Verificar colunas esperadas
        expected_columns = [
            'CIDADE', 'PERÍODO PREVISTO DE TREINAMENTO', 'REALIZOU TREINAMENTO?', 
            'DATA DA INSTALAÇÃO', 'PREFEITURAS DE', 'DATA DO INÍCIO ATEND.', 
            'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Colunas ausentes no Excel: {', '.join(missing_columns)}")

        # Filtrar linhas válidas
        df['CIDADE'] = df['CIDADE'].astype(str).str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        df['PREFEITURAS DE'] = df['PREFEITURAS DE'].astype(str).str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        df['REALIZOU TREINAMENTO?'] = df['REALIZOU TREINAMENTO?'].astype(str).str.strip()

        df = df[df['CIDADE'].notna() & (df['CIDADE'] != '') & (df['CIDADE'] != 'TOTAL')]
        df = df[df['PREFEITURAS DE'].notna() & (df['PREFEITURAS DE'] != '')]
        df = df[df['REALIZOU TREINAMENTO?'].isin(['Sim', 'Não'])]

        # Detectar colunas de meses dinamicamente
        possible_months = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 
                           'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO', 'NOVEMBRO', 'DEZEMBRO']
        months = [m for m in possible_months if m in df.columns]

        # Tratar a coluna PERÍODO PREVISTO DE TREINAMENTO
        def parse_training_period(period):
            if pd.isna(period) or not isinstance(period, str) or period.strip() == '' or period.strip().upper() == 'N-PREV.':
                return pd.NaT, pd.NaT
            try:
                dates = re.split(r'\s*(?:à|a)\s*', period.strip(), flags=re.IGNORECASE)
                if len(dates) != 2:
                    return pd.NaT, pd.NaT
                start_date_str, end_date_str = dates
                start_date_str = start_date_str.strip()
                end_date_str = end_date_str.strip()
                if start_date_str.count('/') == 1:
                    start_date = pd.to_datetime(f"{start_date_str}/2025", format='%d/%m/%Y', errors='coerce')
                else:
                    start_date = pd.to_datetime(start_date_str, format='%d/%m/%Y', errors='coerce')
                if end_date_str.count('/') == 1:
                    end_date = pd.to_datetime(f"{end_date_str}/2025", format='%d/%m/%Y', errors='coerce')
                else:
                    end_date = pd.to_datetime(end_date_str, format='%d/%m/%Y', errors='coerce')
                return start_date, end_date
            except Exception:
                return pd.NaT, pd.NaT

        df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)

        # Converter colunas de datas para datetime
        date_cols = ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')

        # Converter colunas de meses para numérico
        for month in months:
            df[month] = pd.to_numeric(df[month], errors='coerce').fillna(0)

        return df, months
    except Exception as e:
        raise Exception(f"Erro ao carregar o Excel: {str(e)}")