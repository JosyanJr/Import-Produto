import pandas as pd
import os
import sys

def obter_diretorio_base():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

# Obter o diretório base
diretorio_base = obter_diretorio_base()

def formatar_valor(valor):
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)

def gerar_insert_produto(row):
    desc = row['proDescricao']
    ncm = ''.join(filter(str.isdigit, str(row['zzz_proCodigoNCM'])))[:8]
    
    # Colunas e seus valores correspondentes
    columns_values = {
        'proid': row['proid'],
        'proDescricao': f"'{desc[:50]}'",
        'proDescPdv': f"'{desc[:29]}'",
        'proGrupo': row['proGrupo'],
        'proSubGrupo': formatar_valor(row['proSubGrupo']),
        'proFab': formatar_valor(row['proFab']),
        'zzz_proCodigoNCM': ncm,
        'proUsaM2': 0,
        'proUsaPpauta': 0,
        'proControlado': 0
    }
    
    columns = ', '.join(columns_values.keys())
    values = ', '.join(map(str, columns_values.values()))
    
    insert = f"INSERT INTO produto({columns}) VALUES({values}) GO"
    return insert

def gerar_insert_produto_empresa(row):
    id = row['proid']
    Cst2 = str(row['proCodCst2']).zfill(2)
    
    # Colunas e seus valores correspondentes
    columns_values = {
        'empid': 1,
        'preid': id,
        'proid': id,
        'proCodigo': f"'{row['proCodigo']}'",
        'ProCusto': row['ProCusto'],
        'ProVenda': row['ProVenda'],
        'ProUn': f"'{row['ProUn']}'",
        'ProUnTrib': f"'{row['ProUnTrib']}'",
        'proUnComercialId': row['proUnComercialId'],
        'proUnTribId': row['proUnTribId'],
        'proCodCst2': f"'{Cst2}'",
        'proCodCSOSN': f"'{row['proCodCSOSN']}'",
        'proLocalizador': f"'{row['proLocalizador']}'",
        'proListaInvent': -1,
        'proEstoqueMin': 1
    }
    
    columns = ', '.join(columns_values.keys())
    values = ', '.join(map(str, columns_values.values()))
    
    insert = f"INSERT INTO produto_empresa({columns}) VALUES({values}) GO"
    return insert

def gerar_sql_inserts(df):
    inserts = []

    inserts.append('EXEC SP_MSFOREACHTABLE "ALTER TABLE ? NOCHECK CONSTRAINT ALL" GO')

    # Inserts na tabela produto
    inserts.append('SET IDENTITY_INSERT produto ON GO')
    for _, row in df.iterrows():
        inserts.append(gerar_insert_produto(row))
    inserts.append('SET IDENTITY_INSERT produto OFF GO')

    # Inserts na tabela produto_empresa
    inserts.append('SET IDENTITY_INSERT produto_empresa ON GO')
    for _, row in df.iterrows():
        inserts.append(gerar_insert_produto_empresa(row))
    inserts.append('SET IDENTITY_INSERT produto_empresa OFF GO')

    inserts.append('EXEC SP_MSFOREACHTABLE "ALTER TABLE ? CHECK CONSTRAINT ALL" GO')

    return inserts

def salvar_sql_inserts(arquivo, inserts):
    with open(arquivo, 'w', encoding='utf-8') as f:
        for insert in inserts:
            f.write(insert + '\n')

def criar_arquivo_excel_default(caminho_arquivo):
    colunas = [
        'proid','proCodigo', 'proDescricao', 'proGrupo', 'proSubGrupo', 'proFab',
        'zzz_proCodigoNCM', 'ProCusto', 'ProVenda', 'ProUn', 
        'ProUnTrib', 'proUnComercialId', 'proUnTribId', 'proCodCst2',
        'proCodCSOSN', 'proLocalizador'
    ]
    
    df = pd.DataFrame(columns=colunas)
    df.to_excel(caminho_arquivo, index=False, sheet_name='Plan1')

if __name__ == "__main__":
    caminho_arquivo_excel = os.path.join(diretorio_base, "dadosProdutos.xlsx")
    
    if not os.path.exists(caminho_arquivo_excel):
        print(f"Arquivo '{caminho_arquivo_excel}' não encontrado. Criando um arquivo modelo.")
        criar_arquivo_excel_default(caminho_arquivo_excel)
        print(f"Arquivo modelo criado em '{caminho_arquivo_excel}'. Por favor, preencha os dados e execute o script novamente.")
        sys.exit()
    
    df = pd.read_excel(caminho_arquivo_excel, sheet_name='Plan1')
    df = df.fillna('Null')

    inserts = gerar_sql_inserts(df)

    arquivo = os.path.join(diretorio_base, "insertsProdutos2.txt")
    salvar_sql_inserts(arquivo, inserts)
    print(f"Arquivo gerado com sucesso.")
