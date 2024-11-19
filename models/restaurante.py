class Restaurante:
    def __init__(self, pk: int | None, nome: str, email: str, senha: str, comissao: int, login=None):
        self.pk = pk
        self.nome = nome
        self.email = email
        self.senha = senha
        self.comissao = comissao
        self.login = login

    def __str__(self):
        return f'{self.nome}, {self.email}, Comissão: {self.comissao}'
