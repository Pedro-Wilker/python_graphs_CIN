import streamlit as st
import pandas as pd

def render_geral_amplo():
    st.markdown("""
        <h3>Geral Amplo <span class="material-icons" style="vertical-align: middle; color: #004aad;">dashboard</span></h3>
    """, unsafe_allow_html=True)
    
    try:
        # Caminho do arquivo Excel
        excel_file = "C:/Users/re049227/Documents/pythonGraphs/ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx"
        
        # Ler a aba 'Geral-Amplo' diretamente
        df = pd.read_excel(excel_file, sheet_name='Geral-Amplo', engine='openpyxl')
        
        # Normalizar nomes das colunas
        df.columns = df.columns.str.replace('\n', ' ').str.strip().str.replace(r'\s+', ' ', regex=True)
        
        # Verificar colunas esperadas
        expected_columns = [
            'CIDADE', 'DATA DA INSTALAÇÃO', 'APTO PARA INSTALAÇÃO?', 'DATA DO INÍCIO ATEND.',
            'SIT. DA INFRA-ESTRUTURA P/VISITA TÉCNICA', 'DATA DO D.O.', 
            'SITUAÇÃO DO NOVO TERMO DE COOPERAÇÃO', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?',
            'PARECER DA VISITA TÉCNICA', 'DATA DA VISITA TÉCNICA', 'PERÍODO PREVISTO DE TREINAMENTO'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Geral-Amplo': {', '.join(missing_columns)}")
            st.write("Colunas disponíveis no DataFrame:", df.columns.tolist())
            # Adiciona colunas ausentes com valores padrão
            for col in missing_columns:
                if col in ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'DATA DO D.O.', 
                          'DATA DA VISITA TÉCNICA', 'PERÍODO PREVISTO DE TREINAMENTO']:
                    df[col] = pd.NaT
                elif col in ['APTO PARA INSTALAÇÃO?', 'ADEQUEÇÕES APÓS VISITA TÉCNICA REALIZADAS?']:
                    df[col] = False
                else:
                    df[col] = ''
        
        # Converter colunas de datas para datetime
        date_cols = ['DATA DA INSTALAÇÃO', 'DATA DO INÍCIO ATEND.', 'DATA DO D.O.', 'DATA DA VISITA TÉCNICA']
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], format='%d/%m/%Y', errors='coerce')
        
        # Tratar a coluna PERÍODO PREVISTO DE TREINAMENTO
        if 'PERÍODO PREVISTO DE TREINAMENTO' in df.columns:
            def parse_training_period(period):
                if pd.isna(period) or not isinstance(period, str) or period.strip() == '' or period.strip().upper() == 'N-PREV.':
                    return pd.NaT, pd.NaT
                try:
                    import re
                    dates = re.split(r'\s*(?:à|a)\s*', period.strip(), flags=re.IGNORECASE)
                    if len(dates) != 2:
                        return pd.NaT, pd.NaT
                    start_date_str, end_date_str = dates
                    start_date_str = start_date_str.strip()
                    if start_date_str.count('/') == 1:
                        start_date = pd.to_datetime(f"{start_date_str}/2025", format='%d/%m/%Y', errors='coerce')
                    else:
                        start_date = pd.to_datetime(start_date_str, format='%d/%m/%Y', errors='coerce')
                    end_date_str = end_date_str.strip()
                    if end_date_str.count('/') == 1:
                        end_date = pd.to_datetime(f"{end_date_str}/2025", format='%d/%m/%Y', errors='coerce')
                    else:
                        end_date = pd.to_datetime(end_date_str, format='%d/%m/%Y', errors='coerce')
                    return start_date, end_date
                except Exception:
                    return pd.NaT, pd.NaT
            
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['PERÍODO PREVISTO DE TREINAMENTO'].apply(parse_training_period).apply(pd.Series)
        else:
            df['DATA INÍCIO TREINAMENTO'] = pd.NaT
            df['DATA FIM TREINAMENTO'] = pd.NaT
        
        # Exibir o DataFrame
        st.write("Dados da aba Geral-Amplo:")
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Erro ao processar a aba Geral-Amplo: {str(e)}")
        st.write("Verifique se o arquivo 'ACOMPANHAMENTO_CIN_EM_TODO_LUGAR.xlsx' está no diretório correto e contém a aba 'Geral-Amplo' com as colunas esperadas.")