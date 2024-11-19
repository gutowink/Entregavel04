import time
from utils.singleton import Singleton
from utils.utils import Utils
from utils.metodos import Metodos
from models.user import User
from models.venda import Venda

class Client:
    def __init__(self, db, app):
        self.db = db
        self.singleton = Singleton()
        self.app = app
        self.current_user = None

    def show_user_signup(self):  # quase o mesmo métodoo de cadastro do restaurante
        Utils.clear_screen()
        print('> Criar Conta <\n')
        while True:
            user_name = input('Informe seu nome completo: ').title()
            if Metodos.nome_valido(user_name):
                break
            else:
                print('Nome inválido.')

        while True:
            user_email = input('Informe um email: ').lower()
            if Metodos.validar_email(user_email):
                email_usado = self.db.verifica_email(user_email)
                if email_usado is None:
                    break
                else:
                    print(f'O email {user_email} já está em uso.')
            else:
                print('Email inválido.')

        while True:
            user_pwd = input('Informe uma senha: ')
            if Metodos.validar_senha(user_pwd):
                break
            else:
                print('Senha inválida.\n')
                print('A senha precisa ter ao menos:\n')
                print('- 1 minúsculo')
                print('- 1 maiúsculo')
                print('- 1 número')
                print('- 5 caracteres\n')

        new_user = User(None, user_name, user_email, user_pwd, None)
        self.db.create_user(new_user)
        print(f'\nUsuário {user_name} cadastrado com sucesso!')
        time.sleep(2)
        self.app.start_app()

    def show_user_login(self):  # mesmo métodoo de login do restaurante
        Utils.clear_screen()
        print('> Login <\n')
        while True:
            email = input('Informe o email de login: ').lower()
            email_existe = self.db.verifica_email(email)
            if self.db.verifica_email_restaurante(email):
                print('Não tem usuário cadastrado com este email.\n')
                voltar_menu = input('Deseja voltar para o menu inicial? (s/n) ').lower()
                if voltar_menu == 's':
                    self.app.start_app()
                else:
                    continue
            if email_existe is None:
                print('Não tem usuário cadastrado com este email.\n')
                voltar_menu = input('Deseja voltar para o menu inicial? (s/n) ').lower()
                if voltar_menu == 's':
                    self.app.start_app()
                else:
                    continue
            else:
                break

        while True:
            senha = input('Informe a senha de login: ')
            user = self.db.user_login(email, senha)  # armazena o usuário logado
            if user is None:
                print('Senha inválida.\n')
                voltar_menu = input('Deseja voltar para o menu inicial? (s/n) ').lower()
                if voltar_menu == 's':
                    self.app.start_app()
                else:
                    continue
            else:
                self.singleton.set_user(user)
                ultimo_login = self.db.update_user_login(email)  # Atualiza o último 'login' do usuário
                self.singleton.set_last_user_login(ultimo_login)
                break

        print(f'\nBem vindo, {user.nome_completo}\n')
        time.sleep(2)
        self.restaurant_catalog()

    def restaurant_catalog(self):
        Utils.clear_screen()
        print('> Catalogo de Restaurantes <\n')
        restaurants = self.db.get_restaurants_catalog()
        if restaurants is not None:
            biggest_len = Metodos.conta_espaco(restaurants)
            print(f'Os restaurantes recomendados recebem: ️\u2764\uFE0F\n')
            restaurants_id = []
            for restaurant in restaurants:
                espaco_nome = restaurant.nome.ljust(biggest_len)  # Ajusta o nome para o tamanho do maior nome
                restaurants_id.append(str(restaurant.pk))  # salva o 'id' de todos os restaurantes numa lista
                if Metodos.is_recommended(restaurant, restaurants):
                    print(f'   |{str(restaurant.pk).ljust(4)}| {espaco_nome} | \u2764\uFE0F')
                else:
                    print(f'   |{str(restaurant.pk).ljust(4)}| {espaco_nome} |')

            while True:
                restaurant_id = input('\nInforme o ID do restaurante desejado: ')
                if restaurant_id in restaurants_id:  # se o 'id' informado não estiver na lista de 'ids'cadastrados.
                    restaurant = self.db.get_restaurant_by_id(restaurant_id)
                    self.singleton.set_chosen_restaurant(restaurant)  # salva o restaurante no singleton
                    return self.cart()
                elif restaurant_id == '0':
                    self.logout()
                else:
                    print('não existe restaurante com este ID.')
        else:
            print('Não há restaurantes cadastrados ainda.')
            time.sleep(2)
            self.logout()

    def cart(self):
        # pegas as informações necessárias armazenadas no singleton
        restaurant = self.singleton.get_chosen_restaurant()
        user = self.singleton.get_user()

        products = self.db.get_produtos(restaurant.pk)

        produtos_no_carrinho = self.db.get_produtos_carrinho(user.pk)
        if produtos_no_carrinho:
            restaurante_carrinho = produtos_no_carrinho[0].id_restaurante
            if restaurante_carrinho != restaurant.pk:
                print('Você só pode adicionar produtos do mesmo restaurante no carrinho.')
                time.sleep(2)
                return self.restaurant_catalog()

        if products:  # verifica se o restaurante selecionado tem catálogo disponível.
            Utils.clear_screen()
            print(f'\n{restaurant.nome}:')

            self.visualizar_carrinho()  # carrinho

            Metodos.tabela_produtos(products)  # lista de produtos do restaurante
            while True:
                print('\nDigite "A" para voltar à lista de restaurantes ou "F" para finalizar a compra.')
                product_id = input('\nInforme o ID do produto desejado: ')

                if product_id.upper() == 'A':
                    while True:
                        certeza = input('Deseja mesmo abandonar o'
                                        ' carrinho e voltar à lista de restaurantes? (s/n) ').lower()
                        if certeza == 's':  # esvazia o carrinho e volta à lista de restaurantes.
                            self.db.clear_cart(user.pk)
                            return self.restaurant_catalog()
                        elif certeza == 'n':
                            self.cart()
                        else:
                            continue

                elif product_id.upper() == 'F':
                    # verifica os produtos no carrinho do usuário
                    produtos_no_carrinho = self.db.get_produtos_carrinho(user.pk)
                    if produtos_no_carrinho:
                        for produto in produtos_no_carrinho:  # lança a nova venda para todos os produtos do carrinho.
                            new_sell = Venda(None, produto.pk, produto.id_restaurante, produto.id_usuario,
                                             produto.nome_produto, produto.quantidade, produto.preco, produto.total)
                            self.db.venda(new_sell)  # salva a nova venda no banco de dados
                        return self.pedido_concluido()
                    else:
                        print("Não há itens no carrinho para finalizar a venda.")
                        continue

                if Metodos.eh_inteiro(product_id):  # verifica se o usuário inseriu um número
                    product_id = int(product_id)
                    # verifica se este produto está cadastrado no restaurante escolhido.
                    product = self.db.get_produto_id(product_id, restaurant.pk)
                    if product:
                        self.singleton.set_produtos(product)  # salva o produto no singleton
                        break
                    else:
                        print('Produto não encontrado.')
                else:
                    print('Insira um ID válido.')

            while True:
                product = self.singleton.get_produtos()
                quantity = input(f'Informe a quantidade desejada de {product.nome}: ')
                if Metodos.eh_inteiro(quantity):
                    quantity = int(quantity)
                    if quantity > 0:
                        total = quantity * product.preco
                        self.add_product(product, quantity, product.preco, total)  # adiciona produto no carrinho
                        return self.cart()
                    elif quantity == 0:
                        self.db.delete_product(product.pk)  # tira um produto do carrinho
                        print(f'\n{product.nome} removido do carrinho.')
                        return self.cart()
                    else:
                        print('Informe uma quantidade válida.')
                else:
                    print('Informe uma quantidade válida.')
        else:
            Utils.clear_screen()
            print('Este restaurante ainda não tem nenhum produto.')
            time.sleep(2)
            self.restaurant_catalog()

    def add_product(self, product, quantity, price, total):
        # Obter o ID do usuário e do restaurante a partir do Singleton
        user = self.singleton.get_user()
        restaurant = self.singleton.get_chosen_restaurant()

        # Verifica se o produto já está no carrinho para o usuário e restaurante
        item_in_cart = self.db.get_item_carrinho(user.pk, restaurant.pk, product)

        if item_in_cart:
            # se já tiver o item no carrinho somente atualiza a quantidade e total
            new_quantity = item_in_cart.quantidade + quantity
            new_total = new_quantity * item_in_cart.preco
            self.db.update_item_carrinho(item_in_cart.pk, new_quantity, new_total)
        else:
            # se ainda não tiver insere o novo item no carrinho com todos os campos exigidos
            self.db.add_item_carrinho(user.pk, restaurant.pk, product, quantity, price, total)

        print(f'{quantity} - {product.nome} adicionado(s) ao carrinho com sucesso!\n')

    def visualizar_carrinho(self):
        user = self.singleton.get_user()
        produtos_no_carrinho = self.db.get_produtos_carrinho(user.pk)  # produtos no carrinho do respectivo usuário

        if produtos_no_carrinho:
            print('\n> Produtos no carrinho <\n')
            total_carrinho = 0
            for produto in produtos_no_carrinho:  # printa todos os produtos no carrinho
                print(
                    f'{produto.quantidade}x {produto.nome_produto} - Preço: R${produto.preco:.2f}'
                    f' | subtotal: R${produto.total:.2f}')
                total_carrinho += float(produto.total)  # Converte total para float

            print(f'\nValor total do carrinho: R${total_carrinho:.2f}')
        else:
            print('\nO carrinho está vazio.')

    def pedido_concluido(self):
        user = self.singleton.get_user()  # usuário atual
        vendas = self.db.get_venda(user.pk)  # vendas anteriores
        produtos_no_carrinho = self.db.get_produtos_carrinho(user.pk)  # produtos no carrinho
        total_venda = 0
        # restaurant_name: informações do restaurente pelo último produto adicionado ao carrinho.
        restaurant_name = self.db.get_restaurant_by_id(produtos_no_carrinho[0].id_restaurante)
        Utils.clear_screen()
        print(f'\ncompra feita em: {restaurant_name.nome}\n')
        for produto in produtos_no_carrinho:  # printa todas as informações da venda
            print(
                f'{produto.quantidade}x {produto.nome_produto} - Preço: R${produto.preco:.2f}'
                f' | subtotal: R${produto.total:.2f}')
            total_venda += float(produto.total)
        print(f'\nValor total da venda: R${total_venda:.2f}')

        self.db.insert_pedido(produtos_no_carrinho)
        self.db.clear_cart(user.pk)  # limpa o carrinho após realizar a venda

        # Listar compras anteriores do cliente
        print('\nCompras anteriores:')
        if vendas:  # Verifica se há vendas
            ultimo_venda_data_hora = None
            for venda in vendas:
                # caso o horário seja o mesmo se trata da mesma venda e não printa informações repetidas.
                if venda.data_hora != ultimo_venda_data_hora:
                    restaurant = self.db.get_restaurant_by_id(venda.id_restaurante)  # Obtém o nome do restaurante
                    print(f'Restaurante: {restaurant.nome} | Data/Hora: {venda.data_hora}')
                    ultimo_venda_data_hora = venda.data_hora  # ultima venda recebe a venda atual
            input('\nDigite qualquer coisa para voltar ao catálogo de restaurantes.\n')
            return self.restaurant_catalog()
        else:
            print('Nenhuma compra anterior encontrada.')

    def logout(self):
        Utils.clear_screen()
        while True:
            certeza = input('Deseja mesmo encerrar a sessão? (s/n)').lower()
            if certeza == 's':
                self.app.start_app()  # volta para tela inicial
            elif certeza == 'n':
                self.restaurant_catalog()
            else:
                continue
