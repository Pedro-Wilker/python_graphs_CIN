import pandas as pd

# Dados da planilha
data = {
    "ITEM": [
        "Kits de Identificação",
        "Equipes",
        "- Coordenador",
        "- Perito IIPM",
        "- Apoio",
        "- Atendentes",
        "- Motorista",
        "Unidade Escolar Estadual",
        "Tomada padrão novo (3 pinos)",
        "Transporte - Van",
        "Climatização do ambiente",
        "Impressora"
    ],
    "QUANTIDADE": [
        "5 por equipe (Total: 50)",
        "10",
        "10",
        "10",
        "10",
        "50",
        "10",
        "1 por base",
        "Conforme necessidade",
        "10",
        "1 por unidade escolar",
        "10"
    ],
    "UNIDADE": [
        "Kit",
        "Equipe",
        "Pessoa",
        "Pessoa",
        "Pessoa",
        "Pessoa",
        "Pessoa",
        "Unidade",
        "Ponto de energia",
        "Veículo",
        "Sistema",
        "Unidade"
    ],
    "OBSERVAÇÕES": [
        "Total: 50 kits para 10 equipes",
        "Cada equipe com 9 colaboradores",
        "1 por equipe",
        "1 por equipe",
        "1 por equipe",
        "5 por equipe",
        "1 por equipe",
        "Local para execução dos atendimentos",
        "Compatível com equipamentos modernos",
        "1 Van por equipe para locomoção",
        "Ar-condicionado ou similar",
        "1 por equipe"
    ]
}

# Criar DataFrame
df = pd.DataFrame(data)

# Salvar em Excel
file_name = "Planilha_Recursos_Equipes.xlsx"
df.to_excel(file_name, index=False)

print(f"Arquivo '{file_name}' criado com sucesso!")
