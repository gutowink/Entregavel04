import sqlite3
from pandas import DataFrame

from models.restaurante import Restaurante
from models.produto import Produto
from models.user import User
from models.carrinho import Carrinho
from models.venda import Venda
from models.pedido import Pedido

from datetime import datetime, timedelta, timezone


class DB:

    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name, check_same_thread=False)
        self.__setup_tables()

    def __setup_tables(self):
        cur = self.connection.cursor()  # Create a cursor object to interact with the database

        # Create table if it doesn't exist
        cur.execute('''
                    CREATE TABLE IF NOT EXISTS restaurante (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        senha TEXT NOT NULL,
                        comissao INTEGER NOT NULL,
                        login DATETIME
                    )
                    ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS produto (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        preco FLOAT NOT NULL,
                        id_restaurante INTEGER NOT NULL,
                        FOREIGN KEY (id_restaurante) REFERENCES restaurante(id) 
                    )
                    ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS usuario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nome TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        senha TEXT NOT NULL,
                        login DATETIME
                    )
                    ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS carrinho (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_usuario INTEGER NOT NULL,
                        id_restaurante INTEGER NOT NULL,
                        id_produto INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco INTEGER NOT NULL,
                        total FLOAT NOT NULL,
                        FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                        FOREIGN KEY (id_restaurante) REFERENCES restaurante(id),
                        FOREIGN KEY (id_produto) REFERENCES produto(id)
                    )
                    ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS pedido (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario TEXT NOT NULL,
                        id_restaurante INTEGER NOT NULL,
                        id_produto INTEGER NOT NULL,
                        quantidade INTEGER NOT NULL,
                        preco INTEGER NOT NULL,
                        total FLOAT NOT NULL,
                        id_pedido INTEGER NOT NULL,
                        status TEXT DEFAULT 'criado',
                        FOREIGN KEY (usuario) REFERENCES usuario(nome),
                        FOREIGN KEY (id_restaurante) REFERENCES restaurante(id),
                        FOREIGN KEY (id_produto) REFERENCES produto(id)
                    )
                    ''')

        cur.execute('''
                    CREATE TABLE IF NOT EXISTS venda (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_carrinho INTEGER NOT NULL,
                        id_restaurante INTEGER NOT NULL,
                        id_usuario INTEGER NOT NULL,
                        nome TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        valor INTEGER NOT NULL,
                        total FLOAT NOT NULL,
                        data_hora DATETIME,
                        id_venda INTEGER NOT NULL,
                        FOREIGN KEY (id_usuario) REFERENCES usuario(id),
                        FOREIGN KEY (id_restaurante) REFERENCES restaurante(id),
                        FOREIGN KEY (id_carrinho) REFERENCES carrinho(id)
                    )
                    ''')

        cur.execute(''' 
            SELECT 1 FROM usuario WHERE email = ?
        ''', ('admin@admin.com',))
        usuario_existe = cur.fetchone()

        if not usuario_existe:
            cur.execute('''
                        INSERT INTO usuario (nome, email, senha, login) VALUES (?, ?, ?, ?)
            ''', ('Admin', 'admin@admin.com', 'adminpwd123', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        self.connection.commit()  # Commit the transaction

    def is_admin(self, email: str, senha: str):
        cur = self.connection.cursor()
        cur.execute('''
                        SELECT id, nome, email, senha, login 
                        FROM usuario 
                        WHERE email = ? and senha = ? and id = 1
                        ''', (email, senha))
        record = cur.fetchone()
        if record is None:
            return None
        Admin = User(pk=record[0], nome_completo=record[1], email=record[2], password=record[3], login=record[4])
        return Admin

    def get_connection(self):
        return self.connection

    def create_restaurante(self, restaurante: Restaurante):
        cur = self.connection.cursor()
        cur.execute('''
        INSERT INTO restaurante (nome, email, senha, comissao, login) VALUES (?, ?, ?, ?, ?)
        ''', (restaurante.nome, restaurante.email, restaurante.senha,
                         restaurante.comissao, restaurante.login))
        self.connection.commit()

    def create_user(self, user: User):
        cur = self.connection.cursor()
        cur.execute('''
        INSERT INTO usuario (nome, email, senha, login) VALUES (?, ?, ?, ?)
        ''', (user.nome_completo, user.email, user.password, user.login))
        self.connection.commit()

    def create_produto(self, produto: Produto):
        cur = self.connection.cursor()
        cur.execute('''
        INSERT INTO produto (nome, preco, id_restaurante) VALUES (?, ?, ?)
        ''', (produto.nome, produto.preco, produto.id_restaurante))
        self.connection.commit()

    def add_item_carrinho(self, id_usuario: int, id_restaurante: int, produto: Produto, quantidade: int, preco: float,
                          total: float):
        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO carrinho (id_usuario, id_restaurante, id_produto, quantidade, preco, total)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id_usuario, id_restaurante, produto.pk, quantidade, preco, total))

        self.connection.commit()

    def venda(self, venda: Venda):

        local_timezone = timezone(timedelta(hours=-3))  # ajusta ao fuso horário
        local_time = datetime.now(local_timezone)
        data_hora_formatada = local_time.strftime('%Y-%m-%d %H:%M:%S')
        id_venda = int(datetime.now().timestamp())

        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO venda (id_carrinho, id_restaurante, id_usuario, nome, quantidade, valor, total, data_hora, id_venda)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (venda.id_carrinho, venda.id_restaurante, venda.id_usuario, venda.nome, venda.quantidade,
                          venda.valor, venda.total, data_hora_formatada, id_venda))

        self.connection.commit()

    def get_venda(self, user_id):
        cur = self.connection.cursor()

        # Search for the record
        cur.execute('''
                        SELECT id, id_carrinho, id_restaurante, id_usuario, nome, quantidade, valor, total, data_hora
                        FROM venda
                        WHERE id_usuario = ?
                        ORDER BY data_hora DESC
                        ''', (user_id, ))

        records = cur.fetchall()
        if not records:
            return None
        vendas = []
        for record in records:
            venda = Venda(pk=record[0], id_carrinho=record[1], id_restaurante=record[2], id_usuario=record[3],
                          nome=record[4], quantidade=record[5], valor=record[6], total=record[7], data_hora=record[8])
            vendas.append(venda)
        return vendas

    def clear_cart(self, user_id):
        cur = self.connection.cursor()
        cur.execute('DELETE FROM carrinho WHERE id_usuario = ?', (user_id,))
        self.connection.commit()

    def get_restaurante(self, email: str, senha: str):
        cur = self.connection.cursor()

        # Search for the record
        cur.execute('''
                SELECT id, nome, email, senha, comissao
                FROM restaurante 
                WHERE email = ? and senha = ?
                ''', (email, senha))
        record = cur.fetchone()
        if record is None:
            return None
        restaurante = Restaurante(pk=record[0], nome=record[1], email=record[2],
                                  senha=record[3], comissao=record[4])
        return restaurante

    def get_restaurants_catalog(self):
        cur = self.connection.cursor()

        cur.execute('''
                SELECT id, nome, email, senha, comissao
                FROM restaurante
                ORDER BY comissao DESC
                ''')
        records = cur.fetchall()
        if not records:
            return None
        restaurantes = []
        for record in records:
            restaurante = Restaurante(pk=record[0], nome=record[1], email=record[2],
                                      senha=record[3], comissao=record[4])
            restaurantes.append(restaurante)
        return restaurantes

    def get_restaurant_by_id(self, restaurant_id):
        cur = self.connection.cursor()

        # Search for the record
        cur.execute('''
                        SELECT id, nome, email, senha, comissao
                        FROM restaurante 
                        WHERE id = ?
                        ''', (restaurant_id, ))
        record = cur.fetchone()
        if record is None:
            return None
        restaurante = Restaurante(pk=record[0], nome=record[1], email=record[2],
                                  senha=record[3], comissao=record[4])
        return restaurante

    def get_item_carrinho(self, id_usuario: int, id_restaurante: int, produto: Produto):
        cur = self.connection.cursor()
        cur.execute(''' 
            SELECT id, quantidade, preco, total 
            FROM carrinho 
            WHERE id_usuario = ? AND id_restaurante = ? AND id_produto = ? 
        ''', (id_usuario, id_restaurante, produto.pk))

        record = cur.fetchone()
        if record:
            # Retorna uma instância da classe Carrinho
            return Carrinho(
                pk=record[0], id_usuario=id_usuario, id_restaurante=id_restaurante, id_produto=produto.pk,
                quantidade=record[1], preco=record[2], total=record[3])
        return None

    def verifica_email(self, email: str):
        cur = self.connection.cursor()

        # Verifica na tabela restaurante
        cur.execute('''
                SELECT id, nome, email, senha, comissao 
                FROM restaurante 
                WHERE email = ?
                ''', (email,))
        record = cur.fetchone()

        if record is not None:
            return Restaurante(pk=record[0], nome=record[1], email=record[2],
                               senha=record[3], comissao=record[4])

        # Se não encontrou, verifica na tabela usuario
        cur.execute('''
                SELECT id, nome, email, senha 
                FROM usuario 
                WHERE email = ?
                ''', (email,))
        record = cur.fetchone()

        if record is not None:
            return User(pk=record[0], nome_completo=record[1], email=record[2],
                        password=record[3])

        # Se não encontrou em nenhuma das tabelas, retorna None
        return None

    def verifica_email_restaurante(self, email: str):
        cur = self.connection.cursor()

        # Verifica na tabela restaurante
        cur.execute('''
                SELECT id, nome, email, senha, comissao 
                FROM restaurante 
                WHERE email = ?
                ''', (email,))
        record = cur.fetchone()

        if record is not None:
            return Restaurante(pk=record[0], nome=record[1], email=record[2],
                               senha=record[3], comissao=record[4])

        return None

    def verifica_email_user(self, email: str):
        cur = self.connection.cursor()

        cur.execute('''
                        SELECT id, nome, email, senha 
                        FROM usuario 
                        WHERE email = ?
                        ''', (email,))
        record = cur.fetchone()

        if record is not None:
            return User(pk=record[0], nome_completo=record[1], email=record[2],
                        password=record[3])

        return None

    def login(self, email: str, senha: str):
        cur = self.connection.cursor()

        # Search for the record
        cur.execute('''
                SELECT id, nome, email, senha, comissao, login 
                FROM restaurante 
                WHERE email = ? and senha = ?
                ''', (email, senha))
        record = cur.fetchone()
        if record is None:
            return None
        restaurante = Restaurante(pk=record[0], nome=record[1], email=record[2],
                                  senha=record[3], comissao=record[4], login=record[5])
        return restaurante

    def user_login(self, email: str, senha: str):
        cur = self.connection.cursor()

        # Search for the record
        cur.execute('''
                SELECT id, nome, email, senha, login 
                FROM usuario 
                WHERE email = ? and senha = ?
                ''', (email, senha))
        record = cur.fetchone()
        if record is None:
            return None
        user = User(pk=record[0], nome_completo=record[1], email=record[2], password=record[3], login=record[4])
        return user

    def update_login(self, email: str):
        cur = self.connection.cursor()

        cur.execute(''' 
                SELECT login FROM restaurante 
                WHERE email = ?
            ''', (email,))
        login_atual = cur.fetchone()

        local_timezone = timezone(timedelta(hours=-3))  # ajusta ao fuso horário
        local_time = datetime.now(local_timezone)

        # armazena o ultimo login antes de atualizar para o atual
        if login_atual:
            if login_atual[0]:
                ultimo_login = login_atual[0]
            else:
                ultimo_login = None
        else:
            ultimo_login = None

        cur.execute('''
            UPDATE restaurante
            SET login = ?
            WHERE email = ?
        ''', (local_time, email))
        self.connection.commit()

        return ultimo_login

    def update_user_login(self, email: str):
        cur = self.connection.cursor()

        cur.execute('''
                SELECT login 
                FROM usuario 
                WHERE email = ?
            ''', (email,))
        login_atual = cur.fetchone()

        local_timezone = timezone(timedelta(hours=-3))  # ajusta ao fuso horário
        local_time = datetime.now(local_timezone)

        # armazena o ultimo login antes de atualizar para o atual
        if login_atual:
            if login_atual[0]:
                ultimo_login = login_atual[0]
            else:
                ultimo_login = None
        else:
            ultimo_login = None

        cur.execute('''
            UPDATE usuario
            SET login = ?
            WHERE email = ?
        ''', (local_time, email))
        self.connection.commit()

        return ultimo_login

    def update_comissao(self, nova_comissao: int, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                UPDATE restaurante
                SET comissao = ? 
                WHERE id = ?
            ''', (nova_comissao, id_restaurante,))

        self.connection.commit()

        return True

    def update_item_carrinho(self, id_item: int, nova_quantidade: int, novo_total: float):
        cur = self.connection.cursor()
        cur.execute('''
            UPDATE carrinho 
            SET quantidade = ?, total = ? 
            WHERE id = ?
        ''', (nova_quantidade, novo_total, id_item))

        self.connection.commit()

    def get_pedidos(self, id_restaurante):
        cur = self.connection.cursor()
        cur.execute('''
                SELECT id, usuario, id_produto, quantidade, preco, total, id_pedido, status
                FROM pedido WHERE id_restaurante = ?
                ''', (id_restaurante,))

        record = cur.fetchall()

        pedidos = []
        for item in record:
            pedido = Pedido(pk=item[0], usuario=item[1], id_produto=item[2], quantidade=item[3], preco=item[4],
                            total=item[5], id_pedido=item[6], status=item[7], id_restaurante=id_restaurante)
            pedidos.append(pedido)

        return pedidos

    def get_comissao(self):
        cur = self.connection.cursor()
        cur.execute('''
        SELECT MAX(comissao) FROM restaurante  
        ''')

        max_comissao = cur.fetchone()[0]
        return max_comissao

    def get_comissao_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()
        cur.execute('''
            SELECT comissao FROM restaurante WHERE id = ?
        ''', (id_restaurante,))
        resultado = cur.fetchone()
        return resultado[0]

    def get_produtos(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
        SELECT id, nome, preco FROM produto WHERE id_restaurante = ?
        ''', (id_restaurante,))

        record = cur.fetchall()

        produtos = []
        for item in record:
            produto = Produto(pk=item[0], nome=item[1], preco=item[2], id_restaurante=id_restaurante)
            produtos.append(produto)

        return produtos

    def get_produto_id(self, id_produto: int, id_restaurant: int):
        cur = self.connection.cursor()
        cur.execute(''' 
            SELECT id, nome, preco  
            FROM produto 
            WHERE id = ? and id_restaurante = ?
        ''', (id_produto, id_restaurant))
        record = cur.fetchone()
        if record:
            return Produto(pk=record[0], nome=record[1], preco=record[2], id_restaurante=id_restaurant)
        return None

    def get_produtos_carrinho(self, id_usuario):
        cur = self.connection.cursor()

        cur.execute('''
            SELECT c.id, c.id_usuario, c.id_restaurante, c.id_produto, c.quantidade, c.preco, c.total, p.nome
            FROM carrinho AS c
            JOIN produto AS p ON c.id_produto = p.id
            WHERE c.id_usuario = ?
        ''', (id_usuario,))

        registros = cur.fetchall()

        produtos_carrinho = []
        for record in registros:
            carrinho_item = Carrinho(
                pk=record[0], id_usuario=record[1], id_restaurante=record[2], id_produto=record[3],
                quantidade=record[4], preco=record[5], total=record[6], nome_produto=record[7]
            )
            produtos_carrinho.append(carrinho_item)

        return produtos_carrinho

    def delete_produto(self, id_produto: int):
        cur = self.connection.cursor()

        cur.execute(''' 
        DELETE FROM produto WHERE id = ?
        ''', (id_produto,))

        self.connection.commit()

    def delete_product(self, product_id):
        cursor = self.connection.cursor()
        cursor.execute('DELETE FROM carrinho WHERE id_produto = ?', (product_id,))
        self.connection.commit()

    def get_all_products(self):
        cur = self.connection.cursor()
        cur.execute('SELECT id, nome, preco, id_restaurante FROM produto')
        records = cur.fetchall()

        produtos = []
        for item in records:
            produto = Produto(pk=item[0], nome=item[1], preco=item[2], id_restaurante=item[3])
            produtos.append(produto)

        return produtos if produtos else None

    def get_all_pedidos(self):
        cur = self.connection.cursor()
        cur.execute('''SELECT id, usuario, id_produto, quantidade, preco, total, id_pedido, status, id_restaurante
                     FROM pedido''')
        records = cur.fetchall()

        pedidos = []
        for item in records:
            pedido = Pedido(pk=item[0], usuario=item[1], id_produto=item[2], quantidade=item[3], preco=item[4],
                            total=item[5], id_pedido=item[6], status=item[7], id_restaurante=item[8])
            pedidos.append(pedido)

        return pedidos if pedidos else None

    def get_user_name(self, id_usuario: int):
        cur = self.connection.cursor()
        cur.execute('''SELECT nome FROM usuario WHERE id = ?
                        ''', (id_usuario,))
        record = cur.fetchone()
        return record[0] if record else None

    def insert_pedido(self, produtos_no_carrinho):
        cur = self.connection.cursor()
        id_pedido = int(datetime.now().timestamp())  # Identificador único para o pedido

        for item in produtos_no_carrinho:
            user_name = self.get_user_name(item.id_usuario)
            cur.execute('''
                INSERT INTO pedido (usuario, id_restaurante, id_produto, quantidade, preco, total, id_pedido)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_name, item.id_restaurante, item.id_produto, item.quantidade,
                item.preco, item.total, id_pedido
            ))

        self.connection.commit()
        cur.close()

    def get_pedido_id(self, id_restaurante: int):
        cur = self.connection.cursor()
        cur.execute('''
                        SELECT DISTINCT p.id_pedido
                        FROM pedido p
                        WHERE p.status NOT IN ('recusado', 'entregue') AND id_restaurante = ?
                        ''', (id_restaurante,))

        records = cur.fetchall()
        return records

    def get_product_name(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT pd.nome, p.quantidade, p.id_pedido
                    FROM pedido p
                    LEFT JOIN produto pd ON p.id_produto = pd.id
                    WHERE p.id_pedido = ?
        ''', (id_pedido,))

        records = cur.fetchall()
        return records

    def get_pedido_total(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT ROUND(SUM(p.total), 2)
                    FROM pedido p
                    WHERE id_pedido = ?
                    GROUP BY p.id_pedido
        ''', (id_pedido,))

        record = cur.fetchone()
        return record[0]

    def update_status_pedido_aceito(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    UPDATE pedido
                    SET status = 'aceito'
                    WHERE id_pedido = ?
        ''', (id_pedido,))

        self.connection.commit()
        cur.close()

    def update_status_pedido_recusado(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    UPDATE pedido
                    SET status = 'recusado'
                    WHERE id_pedido = ?
                ''', (id_pedido,))

        self.connection.commit()
        cur.close()

    def update_status_pedido_saiu_entrega(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    UPDATE pedido
                    SET status = 'saiu para entrega'
                    WHERE id_pedido = ?
                ''', (id_pedido,))

        self.connection.commit()
        cur.close()

    def update_status_pedido_entregue(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    UPDATE pedido
                    SET status = 'entregue'
                    WHERE id_pedido = ?
                ''', (id_pedido,))

        self.connection.commit()
        cur.close()

    def get_pedido_status_by_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT p.status
                    FROM pedido p
                    WHERE id_restaurante = ?
        ''', (id_restaurante,))

        records = cur.fetchall()
        return records

    def get_pedido_status_by_pedido(self, id_pedido: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT DISTINCT p.status
                    FROM pedido p
                    WHERE id_pedido = ?
        ''', (id_pedido,))

        record = cur.fetchone()
        return record[0] if record else None

    # Relatórios:  todo retornar as consultas para o flask, em forma de gráfico se possivel

    # Relatórios Restaurante:

    # Qual a média de gasto de cada pessoa?
    def media_gasta(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT  u.nome AS Nome,
                        ROUND(AVG(v.total), 2) AS MediaGasta
                    FROM venda v
                    LEFT JOIN usuario u ON u.id = v.id_usuario
                    WHERE v.id_restaurante = ?
                    GROUP BY u.nome
        ''', (id_restaurante,))

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Qual a maior compra (em valor) feita no restaurante?
    def maior_compra_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT u.nome AS Nome,
                           ROUND(SUM(v.total), 2) AS Total
                    FROM venda v
                    LEFT JOIN usuario u ON u.id = v.id_usuario
                    where v.id_restaurante = ?
                    GROUP BY v.id_venda
                    ORDER BY Total DESC
                    LIMIT 1
        ''', (id_restaurante,))

        record = cur.fetchone()
        return record if record else None

    # Qual o maior pedido (em quantidade de itens) feita no restaurante?
    def maior_pedido_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT v.id_venda,
                           SUM(v.quantidade) AS QuantidadeTotal
                    FROM venda v
                    WHERE v.id_restaurante = ? 
                    GROUP BY v.id_venda
                    ORDER BY QuantidadeTotal DESC
                    LIMIT 1
        ''', (id_restaurante,))

        record = cur.fetchone()
        return record if record else None

    # Liste a maior e a menor comissão paga pelo restaurante
    def maior_e_menor_comissao_paga_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    WITH MaiorComissao AS (
                    SELECT ROUND((SUM(v.total) * r.comissao / 100), 2) AS MaiorComissao
                    FROM venda v
                          LEFT JOIN restaurante r ON r.id = v.id_restaurante
                    WHERE v.id_restaurante = ?
                    GROUP BY v.id_venda
                    ORDER BY MaiorComissao DESC
                    LIMIT 1
                    ),
                    MenorComissao AS (
                    SELECT ROUND((SUM(v.total) * r.comissao / 100), 2) AS MenorComissao
                    FROM venda v
                           LEFT JOIN restaurante r ON r.id = v.id_restaurante
                    WHERE v.id_restaurante = ?
                    GROUP BY v.id_venda
                    ORDER BY MenorComissao
                    LIMIT 1
                    ) SELECT ma.MaiorComissao, me.MenorComissao
                      FROM MaiorComissao ma, MenorComissao me
        ''', (id_restaurante, id_restaurante))

        record = cur.fetchone()
        return record if record else None

    # Qual o item mais pedido?
    def item_mais_pedido(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT v.nome AS Nome
                    FROM venda v
                    WHERE v.id_restaurante = ?
                    GROUP BY v.nome
                    ORDER BY COUNT(v.nome) DESC
                    LIMIT 1
        ''', (id_restaurante,))

        record = cur.fetchone()
        return record if record else None

    # Quantos pedidos em cada status? Liste todos os status, mesmo que não haja pedido
    def qnts_pedidos_p_status(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT
                    -- conta cada ocorrência distinta de id_pedido, para não somar vários items do mesmo pedido como pedidos diferentes
                        COUNT(DISTINCT CASE WHEN p.status = 'criado' THEN p.id_pedido END) AS Criado,
                        COUNT(DISTINCT CASE WHEN p.status = 'aceito' THEN p.id_pedido END) AS Aceito,
                        COUNT(DISTINCT CASE WHEN p.status = 'saiu para entrega' THEN p.id_pedido END) AS SaiuParaEntrega,
                        COUNT(DISTINCT CASE WHEN p.status = 'entregue' THEN p.id_pedido END) AS Entregue,
                        COUNT(DISTINCT CASE WHEN p.status = 'recusado' THEN p.id_pedido END) AS Recusado
                    FROM pedido p
                    WHERE id_restaurante = ?
        ''', (id_restaurante,))

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Calcule a quantidade média de pedidos por cada dia da semana. Pivote o resultado.
    def pedidos_dia_semana(self, id_restaurante: int):
        cur = self.connection.cursor()
        cur.execute('''
                    SELECT
                    -- id_venda é um timestamp Epoch Unix, por isso o uso dele para saber os dias da semana.
                        ROUND(AVG(CASE WHEN strftime('%w', datetime(id_venda, 'unixepoch')) = '1' THEN 10 ELSE 0 END), 1) AS Segunda,
                        ROUND(AVG(CASE WHEN strftime('%w', datetime(id_venda, 'unixepoch')) = '2' THEN 10 ELSE 0 END), 1) AS Terça,
                        ROUND(AVG(CASE WHEN strftime('%w', datetime(id_venda, 'unixepoch')) = '3' THEN 10 ELSE 0 END), 1) AS Quarta,
                        ROUND(AVG(CASE WHEN strftime('%w', datetime(id_venda, 'unixepoch')) = '4' THEN 10 ELSE 0 END), 1) AS Quinta,
                        ROUND(AVG(CASE WHEN strftime('%w', datetime(id_venda, 'unixepoch')) = '5' THEN 10 ELSE 0 END), 1) AS Sexta,
                        ROUND(AVG(CASE WHEN strftime('%w', datetime(id_venda, 'unixepoch')) = '6' THEN 10 ELSE 0 END), 1) AS Sábado
                    FROM venda
                    WHERE id_restaurante = ?

        ''', (id_restaurante,))

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Relatórios Admin:

    # Quantidade de restaurantes e clientes cadastrados
    def qntd_restaurante_cliente(self):
        cur = self.connection.cursor()

        cur.execute('''
                    WITH RestauranteClientes AS (
                        SELECT COUNT(*) AS RestaurantesCadastrados
                        FROM restaurante
                    ),
                    QuantidadeClientes AS (
                        SELECT COUNT(*) AS ClientesCadastrados
                        FROM usuario
                    )
                    SELECT *
                    FROM RestauranteClientes, QuantidadeClientes   
        ''')

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Quantidade de clientes únicos que já fizeram um pedido em cada restaurante
    def clientes_unicos_cada_restaurante(self):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT r.nome AS Restaurante,
                           COUNT(DISTINCT usuario) AS ClientesUnicos
                    FROM pedido
                    LEFT JOIN restaurante r ON pedido.id_restaurante = r.id
                    GROUP BY id_restaurante;
        ''')

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Ticket médio por restaurante (valor médio de cada pedido)
    def ticket_medio(self):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT r.nome AS Restaurante,
                           ROUND(AVG(v.total), 2) AS TicketMedio
                    FROM restaurante r
                    LEFT JOIN venda v ON r.id = v.id_restaurante
                    GROUP BY r.id
                    ORDER BY TicketMedio DESC;
        ''')

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Pivote a quantidade de pedidos de cada restaurante (linhas) e meses (colunas)
    def pedidos_restaurante(self):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT r.nome AS NomeRestaurante,
                    -- id_pedido é um timestamp Epoch Unix, por isso o uso dele para saber os dias da semana.
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '01' THEN 1 ELSE 0 END) AS Janeiro,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '02' THEN 1 ELSE 0 END) AS Fevereiro,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '03' THEN 1 ELSE 0 END) AS Março,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '04' THEN 1 ELSE 0 END) AS Abril,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '05' THEN 1 ELSE 0 END) AS Maio,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '06' THEN 1 ELSE 0 END) AS Junho,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '07' THEN 1 ELSE 0 END) AS Julho,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '08' THEN 1 ELSE 0 END) AS Agosto,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '09' THEN 1 ELSE 0 END) AS Setembro,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '10' THEN 1 ELSE 0 END) AS Outubro,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '11' THEN 1 ELSE 0 END) AS Novembro,
                           SUM(CASE WHEN strftime('%m', datetime(p.id_pedido, 'unixepoch')) = '12' THEN 1 ELSE 0 END) AS Dezembro
                    FROM pedido p
                    JOIN restaurante r ON r.id = p.id_restaurante
                    GROUP BY r.nome, p.id_restaurante;
        ''')

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results

    # Crie um insight para ajudar a administração do sistema
    # insight: os 5 (Valor hipotético, pode ser bem mais dependendo do sucesso do aplicativo) clientes que mais gastaram no aplicativo em geral
    # motivo: os clientes que mais gastam no aplicativo vão receber 1 cupom de desconto a cada X tempo, se manterem esta frequência de pedidos.
    def insight(self):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT p.usuario,
                           ROUND(SUM(p.total), 2) AS Total
                    FROM pedido p
                    GROUP BY p.usuario
                    ORDER BY Total DESC
                    LIMIT 5;
        ''')

        cols = [column[0] for column in cur.description]
        results = DataFrame.from_records(data=cur.fetchall(), columns=cols)
        cur.close()
        return results
