import pandas as pd

def aggregate_data(df, months):
    """
    Agrega dados por cidade, tratando duplicatas.
    """
    agg_dict = {month: 'sum' for month in months}
    agg_dict.update({
        'REALIZOU TREINAMENTO?': 'first',
        'DATA DA INSTALAÇÃO': 'min',
        'DATA DO INÍCIO ATEND.': 'min',
        'DATA INÍCIO TREINAMENTO': 'min',
        'DATA FIM TREINAMENTO': 'min',
        'PREFEITURAS DE': 'first'
    })
    return df.groupby('CIDADE').agg(agg_dict).reset_index()