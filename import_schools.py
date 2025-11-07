import pandas as pd
import sqlite3
import os
from db import get_connect

# --------------------------------------------------------
# CONFIGURAÇÕES
# --------------------------------------------------------

CSV_PATH = "data/microdados_ed_basica_2024.csv"   # caminho do seu CSV
COLUNAS = [
    "NU_ANO_CENSO",
    "NO_REGIAO",
    "NO_UF",
    "SG_UF",
    "NO_MUNICIPIO",
    "NO_ENTIDADE",
    "CO_ENTIDADE",
    "CO_CEP"
]

# --------------------------------------------------------
# PASSO 1 – Validar caminhos e pastas
# --------------------------------------------------------

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"Arquivo CSV não encontrado: {CSV_PATH}")

print("Lendo arquivo CSV do INEP...")

# --------------------------------------------------------
# PASSO 2 – Ler o CSV com ENCODING correto
# --------------------------------------------------------

df = pd.read_csv(
    CSV_PATH,
    sep=";",
    encoding="latin1",  # encoding típico dos microdados
    usecols=COLUNAS,
    dtype=str
)

print("CSV carregado com sucesso:")
print(df.head(), "\n")

# --------------------------------------------------------
# PASSO 3 – Normalizar nomes das colunas
# --------------------------------------------------------

df = df.rename(columns={
    "NU_ANO_CENSO": "ano_censo",
    "NO_REGIAO": "regiao",
    "NO_UF": "nome_uf",
    "SG_UF": "uf",
    "NO_MUNICIPIO": "municipio",
    "NO_ENTIDADE": "nome",
    "CO_ENTIDADE": "codigo_inep",
    "CO_CEP": "cep"
})

print("Colunas renomeadas:")
print(df.head(), "\n")

# --------------------------------------------------------
# PASSO 4 – Conectar ao SQLite
# --------------------------------------------------------

con = get_connect()
cur = con.cursor()

print("Limpando tabela 'escolas'...")

# Apaga apenas os dados, mantém estrutura
cur.execute("DELETE FROM escolas;")
con.commit()

print("Importando dados...")

# --------------------------------------------------------
# PASSO 5 – Importar para SQLite
# --------------------------------------------------------

df.to_sql(
    "escolas",
    con,
    if_exists="append",   # insere dados, não recria a tabela!
    index=False
)

# --------------------------------------------------------
# PASSO 6 – Mostrar resumo
# --------------------------------------------------------

cur.execute("SELECT COUNT(*) FROM escolas;")
total = cur.fetchone()[0]

print(f"Importação concluída com sucesso! Total de registros: {total}")

cur.close()
con.close()
