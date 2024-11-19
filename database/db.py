import sqlite3

from models.restaurante import Restaurante
from models.produto import Produto
from models.user import User
from models.carrinho import Carrinho
from models.venda import Venda

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
                    CREATE TABLE IF NOT EXISTS venda (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        id_carrinho INTEGER NOT NULL,
                        id_restaurante INTEGER NOT NULL,
                        id_usuario INTEGER NOT NULL,
                        nome TEXT NOT NULL,
                        quantidade INTEGER NOT NULL,
                        valor INTEGER NOT NULL,
                        total FLOAT NOT NULL,
                        data_hora DATETIME
                    )
                    ''')

        cur.execute(''' 
            SELECT 1 FROM usuario WHERE email = ?
        ''', ('admin@admin.com',))
        usuario_existe = cur.fetchone()

        if not usuario_existe:
            cur.execute('''
                        INSERT INTO usuario (nome, email, senha, login) VALUES (?, ?, ?, ?)
            ''', ('Admin', 'admin@admin.com', 'admin123', datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

        self.connection.commit()  # Commit the transaction

    def is_admin(self, email: str, senha: str):
        cur = self.connection.cursor()
        cur.execute('''
                        SELECT id, nome, email, senha, login 
                        FROM usuario 
                        WHERE email = ? and senha = ?
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

        cur = self.connection.cursor()
        cur.execute('''
            INSERT INTO venda (id_carrinho, id_restaurante, id_usuario, nome, quantidade, valor, total, data_hora)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (venda.id_carrinho, venda.id_restaurante, venda.id_usuario, venda.nome, venda.quantidade,
                          venda.valor, venda.total, data_hora_formatada))

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

