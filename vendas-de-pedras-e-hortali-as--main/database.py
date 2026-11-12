import sqlite3

def conectar():
    return sqlite3.connect("banco.db")

def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produto (
            id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_produto TEXT NOT NULL,
            unidade_medida TEXT NOT NULL,
            preco_venda REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS colheita (
            id_colheita INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER NOT NULL,
            quantidade REAL NOT NULL,
            data_colheita TEXT NOT NULL,
            FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS perda (
            id_perda INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER NOT NULL,
            quantidade REAL NOT NULL,
            motivo TEXT,
            data_perda TEXT NOT NULL,
            FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venda (
            id_venda INTEGER PRIMARY KEY AUTOINCREMENT,
            id_produto INTEGER NOT NULL,
            quantidade REAL NOT NULL,
            valor_total REAL NOT NULL,
            data_venda TEXT NOT NULL,
            FOREIGN KEY (id_produto) REFERENCES produto(id_produto)
        )
    """)

    conexao.commit()
    conexao.close()