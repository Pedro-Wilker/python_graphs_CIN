import streamlit as st
import pandas as pd
from utils.data_utils import load_excel, process_sheet_data

def render_geral_amplo():
    st.subheader("Geral Amplo")
    try:
        df = load_excel('Geral Amplo')
        df = process_sheet_data(df, 'Geral Amplo')
        st.dataframe(df)
    except Exception as e:
        st.error(f"Erro ao processar a aba Geral Amplo: {str(e)}")
        st.stop()