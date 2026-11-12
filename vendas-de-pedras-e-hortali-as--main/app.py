from flask import Flask, render_template, request, redirect
from database import conectar, criar_banco

app = Flask(__name__)

criar_banco()

@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/produtos")
def produtos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM produto")
    produtos = cursor.fetchall()

    conexao.close()

    return render_template(
        "produtos.html",
        produtos=produtos
    )

@app.route("/produtos/cadastrar", methods=["POST"])
def cadastrar_produto():
    nome = request.form["nome"]
    unidade = request.form["unidade"]
    preco = request.form["preco"]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO produto
        (nome_produto, unidade_medida, preco_venda)
        VALUES (?, ?, ?)
    """, (nome, unidade, preco))

    conexao.commit()
    conexao.close()

    return redirect("/produtos")

@app.route("/colheitas")
def colheitas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            colheita.id_colheita,
            produto.nome_produto,
            colheita.quantidade,
            colheita.data_colheita
        FROM colheita
        INNER JOIN produto
        ON colheita.id_produto = produto.id_produto
    """)

    colheitas = cursor.fetchall()

    cursor.execute("SELECT * FROM produto")
    produtos = cursor.fetchall()

    conexao.close()

    return render_template(
        "colheitas.html",
        colheitas=colheitas,
        produtos=produtos
    )

@app.route("/colheitas/cadastrar", methods=["POST"])
def cadastrar_colheita():
    id_produto = request.form["id_produto"]
    quantidade = request.form["quantidade"]
    data_colheita = request.form["data_colheita"]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO colheita
        (id_produto, quantidade, data_colheita)
        VALUES (?, ?, ?)
    """, (id_produto, quantidade, data_colheita))

    conexao.commit()
    conexao.close()

    return redirect("/colheitas")

@app.route("/perdas")
def perdas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            perda.id_perda,
            produto.nome_produto,
            perda.quantidade,
            perda.motivo,
            perda.data_perda
        FROM perda
        INNER JOIN produto
        ON perda.id_produto = produto.id_produto
    """)

    perdas = cursor.fetchall()

    cursor.execute("SELECT * FROM produto")
    produtos = cursor.fetchall()

    conexao.close()

    return render_template(
        "perdas.html",
        perdas=perdas,
        produtos=produtos
    )

@app.route("/perdas/cadastrar", methods=["POST"])
def cadastrar_perda():
    id_produto = request.form["id_produto"]
    quantidade = request.form["quantidade"]
    motivo = request.form["motivo"]
    data_perda = request.form["data_perda"]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO perda
        (id_produto, quantidade, motivo, data_perda)
        VALUES (?, ?, ?, ?)
    """, (id_produto, quantidade, motivo, data_perda))

    conexao.commit()
    conexao.close()

    return redirect("/perdas")

@app.route("/vendas")
def vendas():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            venda.id_venda,
            produto.nome_produto,
            venda.quantidade,
            venda.valor_total,
            venda.data_venda
        FROM venda
        INNER JOIN produto
        ON venda.id_produto = produto.id_produto
    """)

    vendas = cursor.fetchall()

    cursor.execute("SELECT * FROM produto")
    produtos = cursor.fetchall()

    conexao.close()

    return render_template(
        "vendas.html",
        vendas=vendas,
        produtos=produtos
    )

@app.route("/vendas/cadastrar", methods=["POST"])
def cadastrar_venda():
    id_produto = request.form["id_produto"]
    quantidade = float(request.form["quantidade"])
    data_venda = request.form["data_venda"]

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT preco_venda
        FROM produto
        WHERE id_produto = ?
    """, (id_produto,))

    produto = cursor.fetchone()

    if produto:
        preco = float(produto[0])
        valor_total = quantidade * preco

        cursor.execute("""
            INSERT INTO venda
            (id_produto, quantidade, valor_total, data_venda)
            VALUES (?, ?, ?, ?)
        """, (
            id_produto,
            quantidade,
            valor_total,
            data_venda
        ))

        conexao.commit()

    conexao.close()

    return redirect("/vendas")

@app.route("/estoque")
def estoque():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            produto.nome_produto,

            COALESCE(
                (
                    SELECT SUM(quantidade)
                    FROM colheita
                    WHERE colheita.id_produto = produto.id_produto
                ), 0
            ),

            COALESCE(
                (
                    SELECT SUM(quantidade)
                    FROM perda
                    WHERE perda.id_produto = produto.id_produto
                ), 0
            ),

            COALESCE(
                (
                    SELECT SUM(quantidade)
                    FROM venda
                    WHERE venda.id_produto = produto.id_produto
                ), 0
            )

        FROM produto
    """)

    dados = cursor.fetchall()
    estoque = []

    for item in dados:
        nome = item[0]
        colhido = item[1]
        perdido = item[2]
        vendido = item[3]
        disponivel = colhido - perdido - vendido

        estoque.append(
            (nome, colhido, perdido, vendido, disponivel)
        )

    conexao.close()

    return render_template(
        "estoque.html",
        estoque=estoque
    )

@app.route("/relatorios")
def relatorios():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(quantidade), 0)
        FROM colheita
    """)
    total_colhido = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(quantidade), 0)
        FROM perda
    """)
    total_perdido = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(quantidade), 0)
        FROM venda
    """)
    total_vendido = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COALESCE(SUM(valor_total), 0)
        FROM venda
    """)
    total_dinheiro = cursor.fetchone()[0]

    cursor.execute("""
        SELECT
            produto.nome_produto,

            COALESCE(
                (
                    SELECT SUM(quantidade)
                    FROM colheita
                    WHERE colheita.id_produto = produto.id_produto
                ), 0
            ),

            COALESCE(
                (
                    SELECT SUM(quantidade)
                    FROM perda
                    WHERE perda.id_produto = produto.id_produto
                ), 0
            ),

            COALESCE(
                (
                    SELECT SUM(quantidade)
                    FROM venda
                    WHERE venda.id_produto = produto.id_produto
                ), 0
            )

        FROM produto
    """)

    dados = cursor.fetchall()
    produtos = []

    for item in dados:
        nome = item[0]
        colhido = item[1]
        perdido = item[2]
        vendido = item[3]
        disponivel = colhido - perdido - vendido

        produtos.append(
            (nome, colhido, perdido, vendido, disponivel)
        )

    conexao.close()

    return render_template(
        "relatorios.html",
        total_colhido=total_colhido,
        total_perdido=total_perdido,
        total_vendido=total_vendido,
        total_dinheiro=total_dinheiro,
        produtos=produtos
    )

if __name__ == "__main__":
    app.run(debug=True)