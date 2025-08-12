import streamlit as st
import pandas as pd
import plotly.express as px

def render_general_charts(df, months):
    """
    Renderiza os gráficos gerais na página principal.
    """
    st.subheader("Gráficos Gerais")

    # 1. Cidade que mais e menos produziu em cada mês - Gráfico de linhas
    max_min_data = []
    for month in months:
        valid_df = df[df[month] > 0]
        if not valid_df.empty:
            max_city = valid_df.loc[valid_df[month].idxmax(), 'CIDADE'] if valid_df[month].max() > 0 else "Nenhuma"
            max_prod = valid_df[month].max()
            min_city = valid_df.loc[valid_df[month].idxmin(), 'CIDADE'] if valid_df[month].min() >= 0 else "Nenhuma"
            min_prod = valid_df[month].min()
            max_min_data.append({'Mês': month, 'Tipo': 'Máxima', 'Cidade': max_city, 'Produção': max_prod})
            max_min_data.append({'Mês': month, 'Tipo': 'Mínima', 'Cidade': min_city, 'Produção': min_prod})
        else:
            max_min_data.append({'Mês': month, 'Tipo': 'Máxima', 'Cidade': 'Nenhuma', 'Produção': 0})
            max_min_data.append({'Mês': month, 'Tipo': 'Mínima', 'Cidade': 'Nenhuma', 'Produção': 0})

    if max_min_data:
        max_min_df = pd.DataFrame(max_min_data)
        fig_max_min = px.line(max_min_df, x='Mês', y='Produção', color='Tipo', 
                              title='Produção Máxima e Mínima por Mês',
                              hover_data=['Cidade'], text='Cidade')
        fig_max_min.update_traces(mode='lines+markers+text', textposition='top center')
        fig_max_min.update_layout(showlegend=True)
        st.plotly_chart(fig_max_min)
    else:
        st.warning("Nenhum dado de produção disponível nos meses especificados.")

    # 2. Produção geral por mês - Gráfico de colunas
    total_prod = df[months].sum()
    total_prod_df = pd.DataFrame({'Mês': months, 'Produção Total': total_prod})
    fig_total = px.bar(total_prod_df, x='Mês', y='Produção Total', 
                       title='Produção Geral por Mês')
    fig_total.update_traces(texttemplate='%{y}', textposition='outside')
    st.plotly_chart(fig_total)

    # 3. Total de cidades que realizaram treinamento - Gráfico de pizza
    training_count = df['REALIZOU TREINAMENTO?'].value_counts().reset_index()
    training_count.columns = ['Realizou Treinamento', 'Contagem']
    fig_pizza_training = px.pie(training_count, values='Contagem', names='Realizou Treinamento', 
                                title='Cidades Treinadas vs Não Treinadas')
    fig_pizza_training.update_traces(textinfo='label+percent+value')
    st.plotly_chart(fig_pizza_training)