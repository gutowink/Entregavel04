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
        products = my_db.get_pedidos(restaurante.pk)
        return render_template('pedidos.html', pedidos=products, is_admin=False, logged_in=True)
    elif admin:
        return render_template('pedidos.html', pedidos=[], is_admin=True, logged_in=True)
    else:
        return render_template('pedidos.html', pedidos=[], is_admin=False, logged_in=False)

@flask_app.route('/logout')
def logout():
    # remove the email from the session if it's there
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