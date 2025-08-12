import streamlit as st

def check_duplicates(df):
    """
    Verifica cidades duplicadas e exibe um aviso se houver.
    """
    duplicate_cities = df[df['CIDADE'].duplicated(keep=False)]['CIDADE'].unique()
    if len(duplicate_cities) > 0:
        st.warning(f"Cidades duplicadas encontradas: {duplicate_cities.tolist()}. Agregando dados por cidade.")
    return duplicate_cities