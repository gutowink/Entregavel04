import re


class Metodos:

    @staticmethod
    def nome_valido(nome):
        nome_split = nome.split()
        if len(nome) > 10 and len(nome_split) >= 2:
            return True
        return False

    @staticmethod
    def validar_email(email):
        formato_email = r'^[a-zA-Z0-9]+@[a-zA-Z0-9]+\.[a-z]+$'
        if re.match(formato_email, email):
            return True
        return False

    @staticmethod
    def validar_senha(senha):
        formato_senha = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$'
        if re.match(formato_senha, senha) and len(senha) >= 5:
            return True
        return False

    @staticmethod
    def eh_inteiro(numero):
        if numero.isdigit():
            return True
        return False

    @staticmethod
    def validar_nome_produto(nome):
        chars_invalidos = set("0123456789!@#$%^&*()-_=+[]{};:'\",.<>?/\\|`~")  # nome de produtos só podem conter letras
        if len(nome) < 5:
            return False
        for char in nome:
            if char in chars_invalidos:
                return False
        return True

    @staticmethod
    def valida_preco_produto(preco):
        if preco > 0:
            return True
        return False

    @staticmethod
    def eh_float(valor):
        try:
            float(valor)
            return True
        except ValueError:
            return False

    @staticmethod
    def tabela_produtos(produtos: list) -> None:
        cabecalho = ['Id', 'Nome', 'Preço']
        colunas = [len(cabecalho[0]), len(cabecalho[1]), len(cabecalho[2])]

        # Ajusta o tamanho das colunas com base nos produtos
        for produto in produtos:
            if len(str(produto.pk)) > colunas[0]:  # Se o len do código for maior que o cabeçalho 'Id'
                colunas[0] = len(str(produto.pk))

            if len(produto.nome) > colunas[1]:  # Se o len do nome for maior que o cabeçalho 'Nome'
                colunas[1] = len(produto.nome)

            preco_str = f'R$ {produto.preco:.2f}'
            if len(preco_str) > colunas[2]:  # Se o len do preço for maior que o cabeçalho 'Preço'
                colunas[2] = len(preco_str)

        print('')

        # Cálculo da largura da linha da tabela
        tabela_linha = '-'
        for largura in colunas:
            tabela_linha += '-' * (largura + 2) + '-'
        print(tabela_linha)  # Linha superior da tabela

        # Imprime o cabeçalho
        linha = '|'
        for i in range(len(cabecalho)):
            linha += ' ' + cabecalho[i].ljust(colunas[i]) + ' |'
        print(linha)
        print(tabela_linha)  # Linha após o cabeçalho

        # Imprime os dados dos produtos
        for produto in produtos:
            cod = str(produto.pk)
            nome = produto.nome
            preco = f'R$ {produto.preco:.2f}'

            # Printa os dados da tabela. ljust para esquerda e rjust para direita
            print(f'| {cod.ljust(colunas[0])} | {nome.ljust(colunas[1])} | {preco.rjust(colunas[2])} |')

        print(tabela_linha)  # Linha inferior da tabela

    @staticmethod
    def conta_espaco(restaurants: list):
        maior_len = 0
        for restaurant in restaurants:
            restaurant_len = len(restaurant.nome)
            if restaurant_len > maior_len:
                maior_len = restaurant_len
        return maior_len

    @staticmethod
    def is_recommended(restaurant, restaurants: list):
        best_restaurant = restaurants[0]
        if restaurant.nome == best_restaurant.nome:
            return True
        return False
