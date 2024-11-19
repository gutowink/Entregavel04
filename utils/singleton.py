class Singleton:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.comissao_atual = None
            cls._instance.produtos_atual = None
            cls._instance.current_user = None
            cls._instance.chosen_restaurant = None
            cls._instance.current_restaurant_flask = None
            cls._instance.all_products = None
            cls._instance.current_admin = None
        return cls._instance

    def set_comissao(self, comissao):
        self.comissao_atual = comissao

    def get_comissao(self):
        return self.comissao_atual

    def set_produtos(self, produtos):
        self.produtos_atual = produtos

    def get_produtos(self):
        return self.produtos_atual

    def set_user(self, user):
        self.current_user = user

    def get_user(self):
        return self.current_user

    def set_last_login(self, last_login):
        self.last_login = last_login

    def get_last_login(self):
        return self.last_login

    def set_last_user_login(self, last_user_login):
        self.last_user_login = last_user_login

    def get_last_user_login(self):
        return self.last_user_login

    def set_chosen_restaurant(self, chosen_restaurant):
        self.chosen_restaurant = chosen_restaurant

    def get_chosen_restaurant(self):
        return self.chosen_restaurant

    def set_current_restaurant_flask(self, current_restaurant_flask):
        self.current_restaurant_flask = current_restaurant_flask

    def get_current_restaurant_flask(self):
        return self.current_restaurant_flask

    def set_all_products(self, all_products):
        self.all_products = all_products

    def get_all_products(self):
        return self.all_products

    def set_current_admin(self, current_admin):
        self.current_admin = current_admin

    def get_current_admin(self):
        return self.current_admin
