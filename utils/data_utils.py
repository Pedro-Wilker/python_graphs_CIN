import pandas as pd
import re
from datetime import datetime
import numpy as np
import streamlit as st
import os

# Caminho do arquivo Excel local
EXCEL_FILE = r"C:\Users\re049227\Documents\pythonGraphs\ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"

# Definição dos tipos de dados esperados para cada aba
SHEET_CONFIG = {
    'Geral-Amplo': {
        'sheet_name': 'Geral-Amplo',
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
            'DATA ASSINATURA': {'type': 'date', 'format': '%d/%m/%Y'},
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': {'type': 'string'}
        }
    },
    'Lista X': {
        'sheet_name': 'Lista X',
        'columns': {
            'Cidade': {'type': 'string'},
            'Não Informou a estrutura do posto': {'type': 'boolean'},
            'Com Pendência na estrutura do posto': {'type': 'boolean'},
            'Sem pendência na estrutura do posto': {'type': 'boolean'},
            'Sanou pendências indicadas': {'type': 'boolean'},
            'Ag. Visita técnica': {'type': 'boolean'},
            'Parecer da visita técnica': {'type': 'categorical', 'values': ['APROVADO', 'RECUSADO', 'Não teve parecer']},
            'Realizou Treinamento': {'type': 'boolean'},
            'Ag. Publicação no Diário Oficial Estado': {'type': 'boolean'},
            'Publicado no Diário Oficial do Estado': {'type': 'boolean'},
            'Aguardando instalação': {'type': 'boolean'},
            'instalado': {'type': 'boolean'}
        }
    },
    'Geral-Resumo': {
        'sheet_name': 'Geral-Resumo',
        'columns': {
            'CIDADE': {'type': 'string'},
            'DATA DE ANÁLISE': {'type': 'date', 'format': '%d/%m/%Y'},
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': {'type': 'categorical', 'values': ['Sem pendência', 'Com pendência', 'Não informado']},
            'DATA DA VISITA TÉCNICA': {'type': 'date', 'format': '%d/%m/%Y'},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado']},
            'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?': {'type': 'empty'},
            'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES': {'type': 'empty'},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'TURMA': {'type': 'int'},
            'REALIZOU TREINAMENTO?': {'type': 'boolean'},
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': {'type': 'categorical', 'values': ['Publicado D.O.', 'Não Publicado']},
            'DATA DO D.O.': {'type': 'date', 'format': '%d/%m/%Y'},
            'APTO PARA INSTALAÇÃO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'},
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': {'type': 'string'}
        }
    },
    'Visitas Realizadas': {
        'sheet_name': 'Visitas Realizadas',
        'columns': {
            'CIDADE': {'type': 'string'},
            'DATA DE ANÁLISE': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA DA VISITA TÉCNICA': {'type': 'date', 'format': '%d/%m/%Y'},
            'ADEQUAÇÕES APÓS VISITA TÉCNICA REALIZADAS?': {'type': 'empty'}
        }
    },
    'Ag. Visita': {
        'sheet_name': 'Ag. Visita',
        'columns': {
            'CIDADE': {'type': 'string'},
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': {'type': 'categorical', 'values': ['Sem pendência', 'Com pendência', 'Não informado']},
            'DATA DA VISITA TÉCNICA': {'type': 'date', 'format': '%d/%m/%Y'},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado', '']},
            'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?': {'type': 'empty'},
            'DATA DE FINALIZAÇÃO DAS ADEQUAÇÕES': {'type': 'empty'},
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': {'type': 'string'}
        }
    },
    'Ag_info_prefeitura': {
        'sheet_name': 'Ag_info_prefeitura',
        'columns': {
            'CIDADE': {'type': 'string'},
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': {'type': 'categorical', 'values': ['Sem pendência', 'Com pendência', 'Não informado']},
            'DATA DA VISITA TÉCNICA': {'type': 'date', 'format': '%d/%m/%Y'},
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': {'type': 'string'}
        }
    },
    'Publicados': {
        'sheet_name': 'Publicados',
        'columns': {
            'CIDADE': {'type': 'string'},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado']},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'REALIZOU TREINAMENTO?': {'type': 'boolean'},
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': {'type': 'categorical', 'values': ['Publicado D.O.', 'Não Publicado']},
            'DATA DO D.O.': {'type': 'date', 'format': '%d/%m/%Y'},
            'APTO PARA INSTALAÇÃO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'}
        }
    },
    'Ag_Instalacao': {
        'sheet_name': 'Ag_Instalacao',
        'columns': {
            'CIDADE': {'type': 'string'},
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA': {'type': 'categorical', 'values': ['Sem pendência', 'Com pendência', 'Não informado']},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado']},
            'REALIZOU TREINAMENTO?': {'type': 'boolean'},
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': {'type': 'categorical', 'values': ['Publicado D.O.', 'Não Publicado']},
            'DATA DO D.O.': {'type': 'date', 'format': '%d/%m/%Y'},
            'APTO PARA INSTALAÇÃO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'},
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': {'type': 'string'}
        }
    },
    'Instalados': {
        'sheet_name': 'Instalados',
        'columns': {
            'CIDADE': {'type': 'string'},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado']},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': {'type': 'categorical', 'values': ['Publicado D.O.', 'Não Publicado']},
            'DATA DO D.O.': {'type': 'date', 'format': '%d/%m/%Y'},
            'APTO PARA INSTALAÇÃO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'}
        }
    },
    'Funcionando': {
        'sheet_name': 'Funcionando',
        'columns': {
            'CIDADE': {'type': 'string'},
            'DATA DE ANÁLISE': {'type': 'date', 'format': '%d/%m/%Y'},
            'PARECER DA VISITA TÉCNICA': {'type': 'categorical', 'values': ['Aprovado', 'Reprovado']},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO': {'type': 'categorical', 'values': ['Publicado D.O.', 'Não Publicado']},
            'DATA DO D.O.': {'type': 'date', 'format': '%d/%m/%Y'},
            'APTO PARA INSTALAÇÃO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'}
        }
    },
    'Treina-turma': {
        'sheet_name': 'Treina-turma',
        'columns': {
            'CIDADE': {'type': 'string'},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'TURMA': {'type': 'int'},
            'REALIZOU TREINAMENTO?': {'type': 'boolean'}
        }
    },
    'Treina-cidade': {
        'sheet_name': 'Treina-cidade',
        'columns': {
            'CIDADE': {'type': 'string'},
            'PERÍODO PREVISTO DE TREINAMENTO': {'type': 'training_period'},
            'TURMA': {'type': 'int'},
            'REALIZOU TREINAMENTO?': {'type': 'boolean'}
        }
    },
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
            'Código do Posto': {'type': 'string'},
            'PREVISÃO AJUSTE ESTRUTURA P/ VISITA': {'type': 'string'}
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
            'REALIZOU TREINAMENTO?': {'type': 'boolean'},
            'DATA DA INSTALAÇÃO': {'type': 'date', 'format': '%d/%m/%Y'},
            'PREFEITURAS DE': {'type': 'string'},
            'DATA DO INÍCIO ATEND.': {'type': 'date', 'format': '%d/%m/%Y'},
            'ABRIL': {'type': 'float'},
            'MAIO': {'type': 'float'},
            'JUNHO': {'type': 'float'},
            'JULHO': {'type': 'float'},
            'AGOSTO': {'type': 'float'}
        }
    }
}

@st.cache_data
def load_excel(sheet_name, _file_path=EXCEL_FILE):
    """Carrega uma aba específica do arquivo Excel com caching."""
    try:
        # Carrega apenas as colunas definidas em SHEET_CONFIG, se disponíveis
        expected_cols = list(SHEET_CONFIG.get(sheet_name, {}).get('columns', {}).keys())
        df = pd.read_excel(_file_path, sheet_name=sheet_name, engine='openpyxl', usecols=expected_cols if expected_cols else None)
        
        # Limpar quebras de linha e espaços extras nos nomes das colunas
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Limpar quebras de linha nos dados de todas as colunas de string
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: str(x).replace('\n', ' ').strip() if pd.notnull(x) else '')
        
        return df
    except Exception as e:
        raise Exception(f"Erro ao carregar a aba {sheet_name}: {str(e)}")

def parse_training_period(period):
    """Parseia o período de treinamento no formato 'dd/mm a dd/mm/yy' e retorna as datas de início e fim."""
    if pd.isna(period) or period in ['-', '', 'VAZIO', 'N-PREV.', 'nan']:
        return pd.Series(['', ''])
    
    try:
        period = str(period).strip()
        if not period or period in ['-', 'VAZIO', 'N-PREV.']:
            return pd.Series(['', ''])
        
        parts = re.split(r'\s*(?:à|a)\s*', period, flags=re.IGNORECASE)
        if len(parts) != 2:
            return pd.Series(['', ''])
        
        start_date, end_date = parts
        end_parts = end_date.split('/')
        if len(end_parts) == 3:
            year = '20' + end_parts[2] if len(end_parts[2]) == 2 else end_parts[2]
        elif len(end_parts) == 2:
            year = '2025'
        else:
            return pd.Series(['', ''])
        
        start_parts = start_date.split('/')
        if len(start_parts) == 2:
            start_date = f"{start_date}/{year[-2:]}"
        
        start_date = pd.to_datetime(start_date, format='%d/%m/%y', errors='coerce')
        end_date = pd.to_datetime(end_date, format='%d/%m/%y', errors='coerce')
        
        start_date = start_date.strftime('%d/%m/%Y') if pd.notna(start_date) else ''
        end_date = end_date.strftime('%d/%m/%Y') if pd.notna(end_date) else ''
        
        return pd.Series([start_date, end_date])
    except Exception:
        return pd.Series(['', ''])

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
            df[col] = ''  # Adiciona coluna ausente com valor vazio
            continue
        
        col_type = col_config['type']
        if col_type == 'string':
            df[col] = df[col].apply(lambda x: str(x) if pd.notnull(x) else '').replace('nan', '').str.replace('\n', ' ', regex=False).str.strip()
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
        elif col_type == 'empty':
            df[col] = df[col].apply(lambda x: '' if pd.notnull(x) and str(x).strip() in ['-', 'VAZIO', 'nan'] else str(x) if pd.notnull(x) else '')
    
    return df

@st.cache_data
def process_excel_file():
    """Processa todas as abas do arquivo Excel e retorna um dicionário de DataFrames."""
    processed_data = {}
    for sheet_name in SHEET_CONFIG.keys():
        try:
            df = load_excel(sheet_name)
            processed_data[sheet_name] = process_sheet_data(df, sheet_name)
        except Exception as e:
            st.warning(f"Erro ao processar a aba {sheet_name}: {str(e)}")
    return processed_data