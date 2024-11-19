class Pedido:
    def __init__(self, pk: int | None, usuario: str, id_restaurante: int | None,
                 id_produto: int | None, quantidade: int, preco: float, total: float, id_pedido: int, status: str) -> None:
        self.pk = pk
        self.usuario = usuario
        self.id_restaurante = id_restaurante
        self.id_produto = id_produto
        self.quantidade = quantidade
        self.preco = preco
        self.total = total
        self.id_pedido = id_pedido
        self.status = status

    def __str__(self):
        return f'Pedido: {self.quantidade}x {self.id_produto}, Preço unitário: {self.preco}, Total: {self.total}'

