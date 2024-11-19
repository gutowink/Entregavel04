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
    return render_template('index.html')

@flask_app.route('/login', methods=['GET', 'POST'])
def login():
    falha_login = False
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        restaurante = my_db.login(email, password)
        if restaurante is not None:
            Singleton().set_current_restaurant_flask(restaurante)
            session['email'] = request.form['email']
            return redirect(url_for('index'))
        else:
            admin = my_db.is_admin(email, password)
            if admin is not None:
                Singleton().set_current_admin(admin)
                products = my_db.get_all_products()
                Singleton().set_all_products(products)
                session['email'] = request.form['email']
                return redirect(url_for('index'))
            else:
                falha_login = True
    return render_template('login.html',
                           houve_falha=falha_login)
@flask_app.route('/pedidos')
def pedidos():
    restaurante = Singleton().get_current_restaurant_flask()
    admin = Singleton().get_current_admin()
    if restaurante:
        products = my_db.get_produtos(restaurante.pk)
        return render_template('pedidos.html', pedidos=products, is_admin=False, logged_in=True)
    elif admin:
        products = my_db.get_all_products()
        return render_template('pedidos.html', pedidos=products, is_admin=True, logged_in=True)
    else:
        return render_template('pedidos.html', pedidos=[], is_admin=False, logged_in=False)

@flask_app.route('/logout')
def logout():
    # remove the email from the session if it's there
    session.pop('email', None)
    Singleton().set_current_restaurant_flask(None)
    Singleton().set_current_admin(None)
    return redirect(url_for('index'))
