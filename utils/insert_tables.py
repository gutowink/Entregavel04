# insere dados nas tabelas para testes de funcionalidade.

class Inserts:
    @staticmethod
    def insert_tables(conn):
        cur = conn.cursor()

        # Inserir 5 restaurantes
        restaurantes = [
            ('Restaurante A', 'a@rest.com', 'senha123', 10, '2024-01-01 12:00:00'),
            ('Restaurante B', 'b@rest.com', 'senha123', 15, '2024-02-01 12:00:00'),
            ('Restaurante C', 'c@rest.com', 'senha123', 12, '2024-03-01 12:00:00'),
            ('Restaurante D', 'd@rest.com', 'senha123', 18, '2024-04-01 12:00:00'),
            ('Restaurante E', 'e@rest.com', 'senha123', 20, '2024-05-01 12:00:00')
        ]
        cur.executemany('''
            INSERT INTO restaurante (nome, email, senha, comissao, login) 
            VALUES (?, ?, ?, ?, ?)
        ''', restaurantes)

        # Inserir 5 produtos (associados aos restaurantes)
        produtos = [
            ('Hamburguer', 25.50, 1),
            ('Pizza Margherita', 15.75, 1),
            ('Sushi', 35.10, 2),
            ('Lasanha', 45.20, 3),
            ('Frango Frito', 55.30, 4),
            ('Açaí', 30.10, 5),
            ('Coxinha', 28.50, 1),
            ('Pizza Calabresa', 22.00, 2),
            ('Yakissoba', 40.75, 3),
            ('Taco', 33.90, 4),
            ('Bolo de Rolo', 29.99, 5),
            ('Batata Frita', 19.80, 1),
            ('Pizza de Pepperoni', 27.50, 2),
            ('Esfiha', 31.60, 3),
            ('Pão de Queijo', 44.00, 4),
            ('Pastel', 39.50, 5),
            ('Sopa de Mandioca', 18.75, 1),
            ('Feijoada', 35.00, 2),
            ('Tapioca', 47.60, 3),
            ('Churrasco', 25.25, 4),
            ('Salada de Frutas', 50.00, 5),
            ('Sanduíche Natural', 42.30, 1),
            ('Strogonoff', 16.40, 2),
            ('Churros', 48.10, 3),
            ('Bife à Parmegiana', 32.70, 4),
            ('Mousse de Maracujá', 23.50, 5),
            ('Frango Grelhado', 29.20, 1),
            ('Pizza de Frango com Catupiry', 36.80, 2),
            ('Feijão Tropeiro', 54.60, 3),
            ('Carne de Sol', 41.10, 4)
        ]
        cur.executemany('''
            INSERT INTO produto (nome, preco, id_restaurante) 
            VALUES (?, ?, ?)
        ''', produtos)

        # Inserir 5 usuários
        usuarios = [
            ('Usuario A', 'a@user.com', 'senha123', '2024-06-01 12:00:00'),
            ('Usuario B', 'b@user.com', 'senha123', '2024-07-01 12:00:00'),
            ('Usuario C', 'c@user.com', 'senha123', '2024-08-01 12:00:00'),
            ('Usuario D', 'd@user.com', 'senha123', '2024-09-01 12:00:00'),
            ('Usuario E', 'e@user.com', 'senha123', '2024-10-01 12:00:00')
        ]
        cur.executemany('''
            INSERT INTO usuario (nome, email, senha, login) 
            VALUES (?, ?, ?, ?)
        ''', usuarios)

        # 5 pedidos com 3 produtos cada para testes no flask
        pedidos = [
            ('Usuario E', 1, 1, 2, 25.50, 51.00, 1, 'criado'),
            ('Usuario E', 1, 2, 1, 15.75, 15.75, 1, 'criado'),
            ('Usuario E', 1, 12, 3, 19.80, 59.40, 1, 'criado'),

            ('Usuario A', 2, 3, 1, 35.10, 35.10, 2, 'criado'),
            ('Usuario A', 2, 8, 2, 22.00, 44.00, 2, 'criado'),
            ('Usuario A', 2, 13, 4, 27.50, 110.00, 2, 'criado'),

            ('Usuario B', 3, 4, 2, 45.20, 90.40, 3, 'criado'),
            ('Usuario B', 3, 9, 1, 40.75, 40.75, 3, 'criado'),
            ('Usuario B', 3, 19, 3, 47.60, 142.80, 3, 'criado'),

            ('Usuario C', 4, 5, 1, 55.30, 55.30, 4, 'criado'),
            ('Usuario C', 4, 10, 2, 33.90, 67.80, 4, 'criado'),
            ('Usuario C', 4, 15, 4, 44.00, 176.00, 4, 'criado'),

            ('Usuario D', 5, 6, 3, 30.10, 90.30, 5, 'criado'),
            ('Usuario D', 5, 11, 1, 29.99, 29.99, 5, 'criado'),
            ('Usuario D', 5, 20, 2, 25.25, 50.50, 5, 'criado'),

            ('Usuario B', 1, 1, 2, 25.50, 51.00, 6, 'criado'),
            ('Usuario B', 1, 2, 1, 15.75, 15.75, 6, 'criado'),
            ('Usuario B', 1, 12, 3, 19.80, 59.40, 6, 'criado'),

            ('Usuario E', 2, 3, 1, 35.10, 35.10, 7, 'recusado'),
            ('Usuario E', 2, 8, 2, 22.00, 44.00, 7, 'recusado'),
            ('Usuario E', 2, 13, 4, 27.50, 110.00, 7, 'recusado'),

            ('Usuario C', 3, 4, 2, 45.20, 90.40, 8, 'aceito'),
            ('Usuario C', 3, 9, 1, 40.75, 40.75, 8, 'aceito'),
            ('Usuario C', 3, 19, 3, 47.60, 142.80, 8, 'aceito'),

            ('Usuario D', 4, 5, 1, 55.30, 55.30, 9, 'saiu para entrega'),
            ('Usuario D', 4, 10, 2, 33.90, 67.80, 9, 'saiu para entrega'),
            ('Usuario D', 4, 15, 4, 44.00, 176.00, 9, 'saiu para entrega'),

            ('Usuario A', 5, 6, 3, 30.10, 90.30, 10, 'entregue'),
            ('Usuario A', 5, 11, 1, 29.99, 29.99, 10, 'entregue'),
            ('Usuario A', 5, 20, 2, 25.25, 50.50, 10, 'entregue')
        ]
        cur.executemany('''
        INSERT INTO pedido (usuario, id_restaurante, id_produto, quantidade, preco, total, id_pedido, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', pedidos)

        conn.commit()
