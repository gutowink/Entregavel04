class Venda:
    def __init__(self, pk: int | None, id_carrinho: int | None, id_restaurante: int | None,
                 id_usuario: int | None, nome: str, quantidade: int, valor: float,
                 total: float, data_hora=None):
        self.pk = pk
        self.id_carrinho = id_carrinho
        self.id_restaurante = id_restaurante
        self.id_usuario = id_usuario
        self.nome = nome
        self.quantidade = quantidade
        self.valor = valor
        self.total = total
        self.data_hora = data_hora

    def __str__(self):
        return f'Venda: {self.quantidade}x {self.nome}, Preço unitário: {self.valor}, Total: {self.total}'
