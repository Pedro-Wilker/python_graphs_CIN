import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, parse_training_period, parse_date_columns

def render_chefes_posto():
    st.subheader("Chefes de Posto")
    
    try:
        # Load the 'Chefes_Posto' sheet (updated to match the correct capitalization)
        df = load_excel('Chefes_Posto')
        
        # Expected columns
        expected_columns = [
            'CIDADE', 'Nome do chefe de posto', 'Telefone Celular chefe de posto',
            'Link WhatsApp', 'E-mail chefe de posto', 'Data treinamento'
        ]
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            st.warning(f"Colunas ausentes na aba 'Chefes_Posto': {', '.join(missing_columns)}")

        # Parse training period if the column exists
        if 'Data treinamento' in df.columns:
            df[['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']] = df['Data treinamento'].apply(parse_training_period).apply(pd.Series)
        
        # Parse date columns
        date_cols = ['DATA INÍCIO TREINAMENTO', 'DATA FIM TREINAMENTO']
        df = parse_date_columns(df, date_cols)

        # Display the dataframe
        st.dataframe(df)

    except Exception as e:
        st.error(f"Erro ao processar a aba Chefes_Posto: {str(e)}")
        st.write("Verifique se a aba 'Chefes_Posto' existe no arquivo Excel e contém as colunas esperadas.")
        st.stop()