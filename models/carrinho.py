class Carrinho:
    def __init__(self, pk: int | None, id_usuario: int | None, id_restaurante: int | None,
                 id_produto: int | None, quantidade: int, preco: float, total: float, nome_produto: str | None = None):
        self.pk = pk
        self.id_usuario = id_usuario
        self.id_restaurante = id_restaurante
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.preco = preco
        self.total = total
        self.nome_produto = nome_produto

    def __str__(self):
        return f'Carrinho: {self.quantidade}x {self.nome_produto}, Preço unitário: {self.preco}, Total: {self.total}'

