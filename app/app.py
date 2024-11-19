from models.restaurante import Restaurante
from models.produto import Produto
from utils.utils import Utils
from utils.metodos import *
from utils.singleton import Singleton
from app.client import Client

import time
from datetime import datetime


class App:
    def __init__(self, db):
        self.db = db
        self.singleton = Singleton()
        self.usuario_atual = None
        self.client = Client(db, self)

    def start_app(self):
        Utils.clear_screen()
        print('\n"1" Criar Conta')
        print('"2" Login')
        print('"3" Restaurante\n')
        alternativa = input('')

        if alternativa == '1':
            Utils.clear_screen()
            self.client.show_user_signup()
        elif alternativa == '2':
            Utils.clear_screen()
            self.client.show_user_login()
        elif alternativa == '3':
            Utils.clear_screen()
            self.show_main_menu()
        else:
            self.start_app()

    def show_main_menu(self):
        Utils.clear_screen()
        print('\n"1" Cadastrar restaurante')
        print('"2" Login\n')
        alternativa = input('')
        if alternativa == '1':
            Utils.clear_screen()
            self.show_signup_menu()
        elif alternativa == '2':
            Utils.clear_screen()
            self.show_login_menu()
        else:
            self.show_main_menu()

    def show_signup_menu(self):
        # Valida se o nome tem o número mínimo de caracteres e salva
        print('> Cadastro de restaurante <\n')
        nome_restaurante = input('Informe o nome do restaurante: ')
        while len(nome_restaurante) < 10:
            print('O nome precisa ter no mínimo 10 caracteres.')
            nome_restaurante = input('Informe o nome do restaurante: ')

        # Valida se o email é válido e se já está em uso no banco de dados
        while True:
            email_restaurante = input('Informe um email: ').lower()
            if Metodos.validar_email(email_restaurante):
                email_usado = self.db.verifica_email(email_restaurante)
                if email_usado is None:
                    break  # Sai do loop
                else:
                    print(f'O email {email_restaurante} já está em uso.')
            else:
                print('Email inválido.')

        # Valida se a senha segue todas as regras de validação e salva
        while True:
            senha_restaurante = input('Informe uma senha: ')
            if Metodos.validar_senha(senha_restaurante):
                break
            else:
                print('Senha inválida.\n')
                print('A senha precisa ter ao menos:\n')
                print('- 1 minúsculo')
                print('- 1 maiúsculo')
                print('- 1 número')
                print('- 5 caracteres\n')

        # Exibe a maior comissão registrada no sistema e coleta a comissão do novo restaurante
        maior_comissao = self.db.get_comissao()
        if maior_comissao is not None:
            print(f'\nA maior comissão registrada até agora é: {maior_comissao}%')
            print('O restaurante é recomendado com base nas comissões ao aplicativo.\n')
        comissao = input('Informe um valor de comissão para o aplicativo: ')
        while True:
            if Metodos.eh_inteiro(comissao):
                comissao = int(comissao)
                if comissao < 0 or comissao > 100:
                    print('A comissão precisa ser entre 0 e 100%.')
                else:
                    break
            else:
                print('Insira um número inteiro válido.')

            comissao = input('Informe um valor de comissão para o aplicativo: ')

        # Cria o restaurante no banco de dados
        novo_restaurante = Restaurante(None, nome_restaurante, email_restaurante,
                                       senha_restaurante, comissao, None)
        self.db.create_restaurante(novo_restaurante)
        print(f'\nRestaurante {nome_restaurante} cadastrado com sucesso!')
        time.sleep(2)
        self.show_main_menu()  # Volta pro menu inicial após cadastro

    def show_login_menu(self):
        Utils.clear_screen()
        # Valida se o email de 'login' está salvo no banco
        print('> Login <\n')
        while True:
            email = input('Informe o email de login: ').lower()
            email_existe = self.db.verifica_email(email)
            if self.db.verifica_email_user(email):
                print('Não tem restaurante cadastrado com este email.\n')
                voltar_menu = input('Deseja voltar para o menu inicial? (s/n) ').lower()
                if voltar_menu == 's':
                    self.start_app()
                else:
                    continue
            if email_existe is None:
                print('Não tem restaurante cadastrado com este email.\n')
                voltar_menu = input('Deseja voltar para o menu inicial? (s/n) ').lower()
                if voltar_menu == 's':
                    self.start_app()
                else:
                    continue
            else:
                break

        # Valida se a senha de 'login' está salva no banco
        while True:
            senha = input('Informe a senha de login: ')
            usuario = self.db.login(email, senha)  # armazena o usuário logado
            if usuario is None:
                print('Senha inválida.\n')
                voltar_menu = input('Deseja voltar para o menu inicial? (s/n) ').lower()
                if voltar_menu == 's':
                    self.start_app()
                else:
                    continue
            else:
                self.usuario_atual = usuario
                ultimo_login = self.db.update_login(email)  # Atualiza o último 'login' do usuário
                self.singleton.set_last_login(ultimo_login)
                break

        print(f'\nBem vindo, {usuario.nome}')
        time.sleep(2)
        self.painel_restaurante()

    def painel_restaurante(self):
        # Exibe os produtos cadastrados e as opções do restaurante
        Utils.clear_screen()

        produtos = self.db.get_produtos(self.usuario_atual.pk)
        self.singleton.set_produtos(produtos)

        comissao_atual = self.db.get_comissao_restaurante(self.usuario_atual.pk)
        self.singleton.set_comissao(comissao_atual)

        ultimo_login = self.singleton.get_last_login()
        if ultimo_login:
            ultimo_login_formatado = datetime.fromisoformat(ultimo_login).strftime('%d/%m/%Y %H:%M:%S')
        else:
            ultimo_login_formatado = 'N/A'

        if produtos:
            print(f'\n> Painel do Restaurante <\n')
            print(f'Último login: {ultimo_login_formatado}')
            print(f'A comissão atual é: {comissao_atual}%')
            print('Produtos já cadastrados:')
            Metodos.tabela_produtos(produtos)  # Método que chama a tabela e imprime os produtos.

            print('\n"1" Cadastrar produto')
            print('"2" Apagar produto')
            print('"3" Alterar comissão')
            print('"4" Logout\n')
            alternativa = input('')
            if alternativa == '1':
                Utils.clear_screen()
                self.cadastra_produto()
            elif alternativa == '2':
                Utils.clear_screen()
                self.apaga_produto()
            elif alternativa == '3':
                Utils.clear_screen()
                self.altera_comissao()
            elif alternativa == '4':
                Utils.clear_screen()
                self.logout()
            else:
                self.painel_restaurante()
        else:  # Se não houver produtos cadastrados
            print(f'\n> Painel do Restaurante <\n')
            print(f'Último login: {ultimo_login_formatado}')
            print(f'A comissão atual é: {comissao_atual}%')
            print('Nenhum produto cadastrado até o momento.')
            print('\n"1" Cadastrar produto')
            print('"2" Alterar comissão')
            print('"3" Logout\n')

            alternativa = input('')

            if alternativa == '1':
                Utils.clear_screen()
                self.cadastra_produto()
            elif alternativa == '2':
                Utils.clear_screen()
                self.altera_comissao()
            elif alternativa == '3':
                Utils.clear_screen()
                self.logout()
            else:
                self.painel_restaurante()

    def cadastra_produto(self):
        # Coleta e valida o nome e preço do produto para cadastro
        while True:
            nome_produto = input('Informe o nome do produto: ').strip()
            if Metodos.validar_nome_produto(nome_produto):
                break
            else:
                print('Nome de produto inválido.')
        while True:
            preco_produto = input('Informe o valor do produto: ').strip()
            if Metodos.eh_float(preco_produto):
                preco_produto_float = float(preco_produto)
                if Metodos.valida_preco_produto(preco_produto_float):
                    break
                else:
                    print('Preço inválido.')
            else:
                print('Preço inválido.')

        # Insere o novo produto no banco de dados associado ao restaurante logado
        id_restaurante = self.usuario_atual.pk
        novo_produto = Produto(None, nome_produto, preco_produto_float, id_restaurante)
        self.db.create_produto(novo_produto)
        print('Produto cadastrado com sucesso.')

        time.sleep(2)
        self.painel_restaurante()

    def apaga_produto(self):
        # Exibe os produtos cadastrados e permite deletar um deles
        produtos = self.db.get_produtos(self.usuario_atual.pk)
        Metodos.tabela_produtos(produtos)
        id_produto = input('\nInforme o ID do produto que deseja apagar: ')

        if Metodos.eh_inteiro(id_produto):
            id_produto = int(id_produto)
            # Método para verificar se o produto existe
            produto_existente = self.db.get_produto_id(id_produto, self.usuario_atual.pk)
            if produto_existente:
                self.db.delete_produto(id_produto)  # Chama o método delete para apagar o produto
                print(f'Produto com ID {id_produto} apagado com sucesso.')
            else:
                print('Produto não encontrado.')
        else:
            print('Insira um ID válido.')

        time.sleep(2)
        self.painel_restaurante()

    def altera_comissao(self):
        # Coleta e valida a nova comissão do restaurante
        comissao_atual = self.db.get_comissao_restaurante(self.usuario_atual.pk)
        print(f'A comissão atual é: {comissao_atual}%')

        while True:
            nova_comissao = input('Informe a nova comissão: ')
            if Metodos.eh_inteiro(nova_comissao):
                nova_comissao_int = int(nova_comissao)
                if 0 <= nova_comissao_int <= 100:
                    break
                else:
                    print('A comissão precisa ser entre 0 e 100%.')
            else:
                print('Insira um número inteiro válido.')

        id_restaurante = self.usuario_atual.pk
        self.db.update_comissao(nova_comissao, id_restaurante)

        print(f'Comissão atualizada para {nova_comissao}%.')
        time.sleep(2)
        self.painel_restaurante()

    def logout(self):
        while True:
            certeza = input('Deseja mesmo encerrar a sessão? (s/n)').lower()
            if certeza == 's':
                self.usuario_atual = None  # Reseta o valor de usuario atual para não conflitar com outros restaurantes
                self.start_app()  # volta para tela inicial
            elif certeza == 'n':
                self.painel_restaurante()
            else:
                continue
