import plotly.express as px
import pandas as pd
import calendar

def plot_max_min_production(df, months):
    """Gráfico de linhas para produção máxima e mínima por mês."""
    if not all(col in df.columns for col in months + ['CIDADE']):
        return None
    
    max_min_data = []
    for month in months:
        valid_df = df[df[month].notna() & (df[month] > 0)]
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
        fig = px.line(max_min_df, x='Mês', y='Produção', color='Tipo', 
                      title='Produção Máxima e Mínima por Mês',
                      hover_data=['Cidade'], text='Cidade')
        fig.update_traces(mode='lines+markers+text', textposition='top center')
        fig.update_layout(showlegend=True)
        return fig
    return None

def plot_total_production(df, months):
    """Gráfico de colunas para produção geral por mês."""
    if not all(col in df.columns for col in months):
        return None
    
    total_prod = df[months].sum()
    total_prod_df = pd.DataFrame({'Mês': months, 'Produção Total': total_prod})
    fig = px.bar(total_prod_df, x='Mês', y='Produção Total', 
                 title='Produção Geral por Mês')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return fig

def plot_training_pie(df):
    """Gráfico de pizza para total de cidades treinadas vs não treinadas."""
    if 'REALIZOU TREINAMENTO?' not in df.columns:
        return None
    
    training_count = df['REALIZOU TREINAMENTO?'].value_counts().reset_index()
    training_count.columns = ['Realizou Treinamento', 'Contagem']
    fig = px.pie(training_count, values='Contagem', names='Realizou Treinamento', 
                 title='Cidades Treinadas vs Não Treinadas')
    fig.update_traces(textinfo='label+percent+value')
    return fig

def plot_city_production_bar(city_df, months, city):
    """Gráfico de colunas para produção mês a mês de uma cidade."""
    if not all(col in city_df.columns for col in months):
        return None
    
    city_prod = city_df[months].transpose().reset_index()
    city_prod.columns = ['Mês', 'Produção']
    fig = px.bar(city_prod, x='Mês', y='Produção', 
                 title=f'Produção Mês a Mês - {city}')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return fig

def plot_city_production_line(city_df, months, city):
    """Gráfico de linhas para produção mensal de uma cidade."""
    if not all(col in city_df.columns for col in months):
        return None
    
    city_prod = city_df[months].transpose().reset_index()
    city_prod.columns = ['Mês', 'Produção']
    fig = px.line(city_prod, x='Mês', y='Produção', 
                  title=f'Produção Mensal (Linha) - {city}',
                  markers=True, text='Produção')
    fig.update_traces(mode='lines+markers+text', textposition='top center')
    fig.update_layout(showlegend=True)
    return fig

def plot_daily_avg_pie(city_df, months, city):
    """Gráfico de pizza para média de produção diária por mês."""
    if not all(col in city_df.columns for col in months):
        return None
    
    year = 2025
    month_to_num = {
        'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
        'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
    }
    daily_avg = []
    for month in months:
        if month not in month_to_num:
            continue
        days_in_month = calendar.monthrange(year, month_to_num[month])[1]
        prod = city_df[month].iloc[0] if month in city_df.columns and pd.notna(city_df[month].iloc[0]) else 0
        avg = prod / days_in_month if days_in_month > 0 else 0
        daily_avg.append({'Mês': month, 'Média Diária': avg})
    
    daily_avg_df = pd.DataFrame(daily_avg)
    if daily_avg_df.empty:
        return None
    fig = px.pie(daily_avg_df, values='Média Diária', names='Mês', 
                 title=f'Média de Produção Diária por Mês - {city}')
    fig.update_traces(textinfo='label+percent+value')
    return fig

def plot_compare_total(df, months, selected_city):
    """Gráfico de linhas comparando produção total."""
    if not all(col in df.columns for col in months + ['CIDADE']):
        return None
    
    df['Total Produção'] = df[months].sum(axis=1)
    valid_total_df = df[df['Total Produção'] > 0]
    max_city = valid_total_df.loc[valid_total_df['Total Produção'].idxmax(), 'CIDADE'] if not valid_total_df.empty else "Nenhuma"
    min_city = valid_total_df.loc[valid_total_df['Total Produção'].idxmin(), 'CIDADE'] if not valid_total_df.empty else "Nenhuma"
    
    compare_total_df = pd.DataFrame()
    for city in [max_city, selected_city, min_city]:
        city_data = df[df['CIDADE'] == city][months].transpose().reset_index()
        city_data.columns = ['Mês', 'Produção']
        city_data['Cidade'] = city
        compare_total_df = pd.concat([compare_total_df, city_data], ignore_index=True)
    
    if not compare_total_df.empty:
        fig = px.line(compare_total_df, x='Mês', y='Produção', color='Cidade',
                      title=f'Comparação Produção Total: {max_city}, {selected_city}, {min_city}',
                      markers=True, text='Produção')
        fig.update_traces(mode='lines+markers+text', textposition='top center')
        fig.update_layout(showlegend=True)
        return fig
    return None

def plot_compare_month(df, selected_month, selected_city):
    """Gráfico de barras para comparação no mês selecionado."""
    if selected_month not in df.columns or 'CIDADE' not in df.columns:
        return None
    
    month_data = df[['CIDADE', selected_month]].copy()
    month_data['Produção'] = month_data[selected_month]
    valid_month_data = month_data[month_data['Produção'].notna() & (month_data['Produção'] > 0)]
    max_city = valid_month_data.loc[valid_month_data['Produção'].idxmax(), 'CIDADE'] if not valid_month_data.empty else "Nenhuma"
    min_city = valid_month_data.loc[valid_month_data['Produção'].idxmin(), 'CIDADE'] if not valid_month_data.empty else "Nenhuma"
    selected_prod = month_data[month_data['CIDADE'] == selected_city]['Produção'].iloc[0] if not month_data[month_data['CIDADE'] == selected_city].empty else 0
    
    compare_month_df = pd.DataFrame({
        'Cidade': [max_city, selected_city, min_city],
        'Produção': [
            valid_month_data['Produção'].max() if not valid_month_data.empty else 0,
            selected_prod,
            valid_month_data['Produção'].min() if not valid_month_data.empty else 0
        ]
    })
    fig = px.bar(compare_month_df, x='Cidade', y='Produção',
                 title=f'Comparação no Mês {selected_month}: {max_city}, {selected_city}, {min_city}')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return fig

def plot_compare_cities_bar(compare_df, months, selected_cities):
    """Gráfico de colunas para comparação de cidades."""
    if not all(col in compare_df.columns for col in months + ['CIDADE']):
        return None
    
    compare_prod_df = pd.DataFrame()
    for city in selected_cities:
        city_data = compare_df[compare_df['CIDADE'] == city][months].transpose().reset_index()
        city_data.columns = ['Mês', 'Produção']
        city_data['Cidade'] = city
        compare_prod_df = pd.concat([compare_prod_df, city_data], ignore_index=True)
    
    fig = px.bar(compare_prod_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                 title=f'Produção Mês a Mês - Comparação')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return fig

def plot_compare_cities_line(compare_df, months, selected_cities):
    """Gráfico de linhas para comparação de cidades."""
    if not all(col in compare_df.columns for col in months + ['CIDADE']):
        return None
    
    compare_prod_df = pd.DataFrame()
    for city in selected_cities:
        city_data = compare_df[compare_df['CIDADE'] == city][months].transpose().reset_index()
        city_data.columns = ['Mês', 'Produção']
        city_data['Cidade'] = city
        compare_prod_df = pd.concat([compare_prod_df, city_data], ignore_index=True)
    
    fig = px.line(compare_prod_df, x='Mês', y='Produção', color='Cidade',
                  title=f'Produção Mensal (Linha) - Comparação',
                  markers=True, text='Produção')
    fig.update_traces(mode='lines+markers+text', textposition='top center')
    fig.update_layout(showlegend=True)
    return fig

def plot_compare_cities_daily_avg(compare_df, months, selected_cities):
    """Gráfico de barras para média diária de produção por cidade."""
    if not all(col in compare_df.columns for col in months + ['CIDADE']):
        return None
    
    year = 2025
    month_to_num = {
        'JANEIRO': 1, 'FEVEREIRO': 2, 'MARÇO': 3, 'ABRIL': 4, 'MAIO': 5, 'JUNHO': 6,
        'JULHO': 7, 'AGOSTO': 8, 'SETEMBRO': 9, 'OUTUBRO': 10, 'NOVEMBRO': 11, 'DEZEMBRO': 12
    }
    daily_avg_comp = []
    for city in selected_cities:
        city_row = compare_df[compare_df['CIDADE'] == city]
        for month in months:
            if month not in month_to_num:
                continue
            days_in_month = calendar.monthrange(year, month_to_num[month])[1]
            prod = city_row[month].sum() if not city_row.empty and pd.notna(city_row[month].iloc[0]) else 0
            avg = prod / days_in_month if days_in_month > 0 else 0
            daily_avg_comp.append({'Mês': month, 'Média Diária': avg, 'Cidade': city})
    
    daily_avg_comp_df = pd.DataFrame(daily_avg_comp)
    if daily_avg_comp_df.empty:
        return None
    fig = px.bar(daily_avg_comp_df, x='Mês', y='Média Diária', color='Cidade', barmode='group',
                 title=f'Média de Produção Diária por Mês - Comparação')
    fig.update_traces(texttemplate='%{y:.2f}', textposition='outside')
    return fig

def plot_compare_cities_month(compare_df, selected_month, selected_cities):
    """Gráfico de barras para comparação de cidades em um mês específico."""
    if selected_month not in compare_df.columns or 'CIDADE' not in compare_df.columns:
        return None
    
    month_comp_data = compare_df[['CIDADE', selected_month]].copy()
    month_comp_data['Produção'] = month_comp_data[selected_month]
    fig = px.bar(month_comp_data, x='CIDADE', y='Produção',
                 title=f'Comparação no Mês {selected_month}')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return fig

def plot_compare_dates_bar(filtered_df, months, filter_type):
    """Gráfico de colunas para comparação por datas."""
    if not all(col in filtered_df.columns for col in months + ['CIDADE']):
        return None
    
    compare_date_df = pd.DataFrame()
    for city in filtered_df['CIDADE']:
        city_data = filtered_df[filtered_df['CIDADE'] == city][months].transpose().reset_index()
        city_data.columns = ['Mês', 'Produção']
        city_data['Cidade'] = city
        compare_date_df = pd.concat([compare_date_df, city_data], ignore_index=True)

    fig = px.bar(compare_date_df, x='Mês', y='Produção', color='Cidade', barmode='group',
                 title=f'Produção Mês a Mês - Comparação por {filter_type}')
    fig.update_traces(texttemplate='%{y}', textposition='outside')
    return fig

def plot_compare_dates_line(filtered_df, months, filter_type):
    """Gráfico de linhas para comparação por datas."""
    if not all(col in filtered_df.columns for col in months + ['CIDADE']):
        return None
    
    compare_date_df = pd.DataFrame()
    for city in filtered_df['CIDADE']:
        city_data = filtered_df[filtered_df['CIDADE'] == city][months].transpose().reset_index()
        city_data.columns = ['Mês', 'Produção']
        city_data['Cidade'] = city
        compare_date_df = pd.concat([compare_date_df, city_data], ignore_index=True)

    fig = px.line(compare_date_df, x='Mês', y='Produção', color='Cidade',
                  title=f'Produção Mensal (Linha) - Comparação por {filter_type}',
                  markers=True, text='Produção')
    fig.update_traces(mode='lines+markers+text', textposition='top center')
    fig.update_layout(showlegend=True)
    return fig