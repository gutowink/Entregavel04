class Produto:
    def __init__(self, pk: int | None, nome: str, preco: float, id_restaurante: int):
        self.pk = pk
        self.nome = nome
        self.preco = preco
        self.id_restaurante = id_restaurante

    def __str__(self):
        return f'{self.nome}, {self.preco}'
