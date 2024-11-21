import sqlite3
from database.db import DB

# todo retornar resultados para flask em... ?graficos?
# todo 99/133/151/158

class Relatorios:
    def __init__(self, db):
        self.db = db
        self.connection = sqlite3.connect(db, check_same_thread=False)

    # Qual a média de gasto de cada pessoa?
    def media_gasta(self, id_restaurante : int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT  u.nome AS Nome,
                        ROUND(AVG(v.total), 2) AS MediaGasta
                    FROM venda v
                    LEFT JOIN usuario u ON u.id = v.id_usuario
                    WHERE v.id_restaurante = ?
                    GROUP BY u.nome
        ''', (id_restaurante,))

    # Qual a maior compra (em valor) feita no restaurante?
    def maior_compra_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT SUM(v.total) AS Total
                    FROM venda v
                    where v.id_restaurante = ?
                    GROUP BY v.id_pedido
                    ORDER BY Total DESC
                    LIMIT 1
        ''', (id_restaurante,))

    # Qual o maior pedido (em quantidade de itens) feita no restaurante?
    def maior_pedido_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT v.id_pedido,
                           SUM(v.quantidade) AS QuantidadeTotal
                    FROM venda v
                    WHERE v.id_restaurante = ? 
                    GROUP BY v.id_pedido
                    ORDER BY QuantidadeTotal DESC
                    LIMIT 1
        ''', (id_restaurante,))

    # Liste a maior e a menor comissão paga pelo restaurante
    def maior_e_menor_comissao_paga_restaurante(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT
                        ROUND(SUM(v.total), 2) AS TotalComComissao,
                        ROUND(SUM(v.total) - (SUM(v.total) * r.comissao / 100), 2) AS TotalSemComissao,
                        ROUND((SUM(v.total) * r.comissao / 100), 2) AS DiferencaComissao
                    FROM venda v
                    LEFT JOIN restaurante r ON r.id = v.id_restaurante
                    WHERE v.id_restaurante = ?
                    GROUP BY v.id_pedido
                    ORDER BY DiferencaComissao DESC -- para saber a maior e a menor comissão vou pegar o primeiro e ultimo elemento da consulta.
        ''', (id_restaurante,))

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

    # Quantos pedidos em cada status? Liste todos os status, mesmo que não haja pedido
    def qnts_pedidos_p_status(self, id_restaurante: int):
        cur = self.connection.cursor()

        cur.execute('''
                    SELECT
                        COUNT(DISTINCT CASE WHEN p.status = 'criado' THEN p.id_pedido END) AS Criado,
                        COUNT(DISTINCT CASE WHEN p.status = 'aceito' THEN p.id_pedido END) AS Aceito,
                        COUNT(DISTINCT CASE WHEN p.status = 'saiu para entrega' THEN p.id_pedido END) AS SaiuParaEntrega,
                        COUNT(DISTINCT CASE WHEN p.status = 'entregue' THEN p.id_pedido END) AS Entregue,
                        COUNT(DISTINCT CASE WHEN p.status = 'rejeitado' THEN p.id_pedido END) AS Rejeitado
                    FROM pedido p
                    WHERE id_restaurante = ?
        ''', (id_restaurante,))

    # Calcule a quantidade média de pedidos por cada dia da semana. Pivote o resultado.
    def pedidos_dia_semana(self, id_restaurante : int):
        cur = self.connection.cursor()
        # todo decidir se vai ficar este select mesmo ou tem melhor
        cur.execute('''
                    SELECT
                        AVG(CASE WHEN strftime('%w', datetime(id_pedido, 'unixepoch')) = '0' THEN 1 ELSE 0 END) AS Segunda,
                        AVG(CASE WHEN strftime('%w', datetime(id_pedido, 'unixepoch')) = '1' THEN 1 ELSE 0 END) AS Terça,
                        AVG(CASE WHEN strftime('%w', datetime(id_pedido, 'unixepoch')) = '2' THEN 1 ELSE 0 END) AS Quarta,
                        AVG(CASE WHEN strftime('%w', datetime(id_pedido, 'unixepoch')) = '3' THEN 1 ELSE 0 END) AS Quinta,
                        AVG(CASE WHEN strftime('%w', datetime(id_pedido, 'unixepoch')) = '4' THEN 1 ELSE 0 END) AS Sexta,
                        AVG(CASE WHEN strftime('%w', datetime(id_pedido, 'unixepoch')) = '5' THEN 1 ELSE 0 END) AS Sábado
                    FROM venda
                    WHERE id_restaurante = ?

        ''', (id_restaurante,))

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

    # Quantidade de clientes únicos que já fizeram um pedido em cada restaurante
    def clientes_unicos_cada_restaurante(self):
        cur = self.connection.cursor()
        # todo fazer consulta

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

    # Pivote a quantidade de pedidos de cada restaurante (linhas) e meses (colunas)
    def pedidos_restaurante(self):
        cur = self.connection.cursor()
        #todo fazer consulta

    # Crie um insight para ajudar a administração do sistema
    # insight: os 5 (Valor hipotético, pode ser bem mais dependendo do sucesso do aplicativo) clientes que mais gastaram no aplicativo em geral
    # motivo: os clientes que mais gastam no aplicativo vão receber 1 cupom de desconto a cada X tempo, se manterem esta frequência de pedidos.
    def insight(self):
        cur = self.connection.cursor()
        #todo fazer consulta

    def teste(self):
        pedidos = self.db.get_all_pedidos()
        for pedido in pedidos:
            print(pedido.id_produto)

db_instance = DB(r'F:\pycharm\entregavel04\GulaExpress.db')
relatorios = Relatorios(db_instance)
relatorios.teste()