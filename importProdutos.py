import pandas as pd

def gerar_sql_inserts(df):
    inserts = []

    # Comandos iniciais
    inserts.append('EXEC SP_MSFOREACHTABLE "ALTER TABLE ? NOCHECK CONSTRAINT ALL" GO')

    # Inserts na tabela produto
    inserts.append('SET IDENTITY_INSERT produto ON GO')
    for index, row in df.iterrows():
        id = row['proid']
        desc = row['proDescricao'][:50]
        insert = f"INSERT INTO produto(proid, proDescricao, proDescPdv, proUsaM2, proUsaPpauta, proControlado) VALUES({id}, '{desc}', '{desc[:29]}', 0, 0, 0) go"
        inserts.append(insert)
    inserts.append('SET IDENTITY_INSERT produto OFF go')

    # Inserts na tabela produto_empresa
    inserts.append('SET IDENTITY_INSERT produto_empresa ON GO')
    for index, row in df.iterrows():
        id = row['proid']
        Cst2 = str(row['proCodCst2']).zfill(2)
        insert = f"insert into produto_empresa(empid, preid, proid, proCodigo, ProCusto, ProVenda, ProUn, ProUnTrib, proUnComercialId, proUnTribId, {Cst2}, proCodCSOSN, proListaInvent, proEstoqueMin) VALUES(1, {id}, {id}, {row['proCodigo']}, {row['ProCusto']}, {row['ProVenda']}, '{row['ProUn']}', '{row['ProUnTrib']}', {row['proUnComercialId']}, {row['proUnTribId']}, '{row['proCodCst2']}', {row['proCodCSOSN']}, '-1', 1) go"
        inserts.append(insert)
    inserts.append('SET IDENTITY_INSERT produto_empresa OFF GO')

    # Comandos finais
    inserts.append('SET IDENTITY_INSERT fabricante OFF go')
    inserts.append('EXEC SP_MSFOREACHTABLE "ALTER TABLE ? CHECK CONSTRAINT ALL" GO')

    return inserts

#função para salvar o arquivo
def salvar_sql_inserts(arquivo, inserts):
    with open(arquivo, 'w') as f:
        for insert in inserts:
            f.write(insert + '\n')

if __name__ == "__main__":
    # Carregar os dados do Excel
    df = pd.read_excel('dadosProdutos.xlsx', sheet_name='Plan1')

    # Gerar os inserts ao executar
    inserts = gerar_sql_inserts(df)

    # Salvar os inserts em um arquivo
    arquivo = 'insertsProdutos.txt'
    salvar_sql_inserts(arquivo, inserts)
    print(f"Arquivo {arquivo} gerado com sucesso.")
