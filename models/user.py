class User:
    def __init__(self, pk: int | None, nome_completo: str, email: str, password: str, login=None):
        self.pk = pk
        self.nome_completo = nome_completo
        self.email = email
        self.password = password
        self.login = login

    def __str__(self):
        return f'{self.email}'