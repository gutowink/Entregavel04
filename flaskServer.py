from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import session
from database.db import DB
from utils.singleton import Singleton

my_db = DB('GulaExpress.db')

flask_app = Flask(__name__)
flask_app.secret_key = b'c6#P3hZ"J7Kw\n\xda]/'

@flask_app.route('/')
def index():
    admin = Singleton().get_current_admin()
    if admin is not None:
        return render_template('index.html', is_admin=True)
    else:
        return render_template('index.html', is_admin=False)

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    falha_login = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        restaurante = my_db.login(email, password)
        admin = my_db.is_admin(email, password)
        if restaurante is not None:
            Singleton().set_current_restaurant_flask(restaurante)
            session['email'] = request.form['email']
            return render_template('index.html',
                                   houve_falha=falha_login, is_admin=False)
        elif admin is not None:
            Singleton().set_current_admin(admin)
            products = my_db.get_all_pedidos()
            Singleton().set_all_products(products)
            session['email'] = request.form['email']
            return render_template('index.html',
                                   houve_falha=falha_login, is_admin=True)
        else:
            falha_login = True
    return render_template('login.html',
                           houve_falha=falha_login)
@flask_app.route('/pedidos')
def pedidos():
    restaurante = Singleton().get_current_restaurant_flask()
    admin = Singleton().get_current_admin()
    if restaurante:
        p_pedidos = my_db.get_pedido_id(restaurante.pk)
        pedidos_info = []  # Lista para armazenar informações agrupadas de pedidos

        for pedido_id in p_pedidos:
            pedido_id = pedido_id[0]  # Extrai o ID do pedido
            total = my_db.get_pedido_total(pedido_id)  # pega o total do pedido
            status = my_db.get_pedido_status_by_pedido(pedido_id)
            products = my_db.get_product_name(pedido_id)  # Obtém os produtos do pedido atual
            products_info = []  # Lista para os produtos desse pedido

            for product in products:
                nome = product[0]
                quantidade = product[1]
                products_info.append({'nome': nome, 'quantidade': quantidade})

            pedidos_info.append({'id_pedido': pedido_id,'total': total,'status': status,'product_info': products_info})

        return render_template('pedidos.html', pedidos=pedidos_info, is_admin=False, logged_in=True)
    elif admin:
        return render_template('pedidos.html', pedidos=[], is_admin=True, logged_in=True)
    else:
        return render_template('pedidos.html', pedidos=[], is_admin=False, logged_in=False)

@flask_app.route('/alterar_status/<int:pedido_id>/<novo_status>', methods=['POST'])
def alterar_status(pedido_id, novo_status):
    if novo_status == 'aceito':
        my_db.update_status_pedido_aceito(pedido_id)
    elif novo_status == 'saiu_para_entrega':
        my_db.update_status_pedido_saiu_entrega(pedido_id)
    elif novo_status == 'entregue':
        my_db.update_status_pedido_entregue(pedido_id)
    else:
        my_db.update_status_pedido_recusado(pedido_id)
    return redirect(url_for('pedidos'))

@flask_app.route('/logout')
def logout():
    session.pop('email', None)
    Singleton().set_current_restaurant_flask(None)
    Singleton().set_current_admin(None)
    return redirect(url_for('index'))

@flask_app.route('/relatorios/admin')
def relatorios_admin():
    admin = Singleton().get_current_admin()
    if admin is not None:
        return render_template('relatorios_admin.html', is_admin=True)
    else:
        return render_template('relatorios_admin.html', is_admin=False)

@flask_app.route('/relatorios/restaurante')
def relatorios_restaurante():
    restaurante = Singleton().get_current_restaurant_flask()
    if restaurante is not None:
        return render_template('relatorios_restaurante.html', is_restaurant=True)
    else:
        return render_template('relatorios_restaurante.html', is_restaurant=False)

#  @flask_app.route('/relatorios/restaurante')
#  def relatorios_restaurante():
#      restaurante = Singleton().get_current_restaurant_flask()
#      admin = Singleton().get_current_admin()
#      if restaurante is not None:
#          return render_template('relatorios_restaurante.html', is_restaurant=True, is_admin=False)
#      elif admin is not None:
#          return render_template('relatorios_restaurante.html', is_restaurant=False, is_admin=True)
#      else:
#          return render_template('relatorios_restaurante.html', is_restaurant=False, is_admin=False)

# todo tela de relatórios para restaurante e admin

# todo botões interativos pedidos restaurante
    #  Em 'criado’s coloque as opções ‘aceitar’ e ‘rejeitar’
    # - Em ‘aceito’s coloque a opção ‘saiu para entrega’
    # - Em ‘saiu para entrega’ coloque a opção ‘entregue’