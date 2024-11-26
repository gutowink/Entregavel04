from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import session
from database.db import DB
from utils.singleton import Singleton
from utils.bokehgraph import *

my_db = DB('GulaExpress.db')
bk = Bokeh()

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
        restaurante = my_db.login(email, password)  # verifica se é um restarante
        admin = my_db.is_admin(email, password)  # verifica se é um admin
        if restaurante is not None:
            Singleton().set_current_restaurant_flask(restaurante)  # armazena o restaurente no singleton
            session['email'] = request.form['email']
            return render_template('index.html',
                                   houve_falha=falha_login, is_admin=False)
        elif admin is not None:
            Singleton().set_current_admin(admin)
            products = my_db.get_all_pedidos()
            Singleton().set_all_products(products)  # armazena todos os prdotuso no singleton
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
        pedidos_info = []  # Lista para armazenar informações de pedidos

        for pedido_id in p_pedidos:
            pedido_id = pedido_id[0]  # ID do pedido
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
    # altera o status do pedido no banco de dados
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
    # limpa as informaçõs do usuário quando faz o logout e redireciona para a tela de login
    session.pop('email', None)
    Singleton().set_current_restaurant_flask(None)
    Singleton().set_current_admin(None)
    return redirect(url_for('login'))

@flask_app.route('/relatorios/admin')
def relatorios_admin():
    admin = Singleton().get_current_admin()
    if admin is not None:

        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        # consultas para os relatórios
        qntd_restaurante_cliente = my_db.qntd_restaurante_cliente()
        graph5 = bk.admin_graph5(qntd_restaurante_cliente)

        clientes_unicos = my_db.clientes_unicos_cada_restaurante()
        graph1 = bk.admin_graph1(clientes_unicos)

        ticket_medio = my_db.ticket_medio()
        graph2 = bk.admin_graph2(ticket_medio)

        pedidos_restaurantes = my_db.pedidos_restaurante()
        graph3 = bk.admin_graph3(pedidos_restaurantes)

        insight = my_db.insight()
        graph4 = bk.admin_graph4(insight)

        data = {  # salva as informaçõs num dicionário para melhor organização
            'qntd_restaurante_cliente': qntd_restaurante_cliente,
            'graph1': graph1,
            'graph2': graph2,
            'graph3': graph3,
            'graph4': graph4,
            'graph5': graph5
        }

        return render_template('relatorios_admin.html', is_admin=True,
                               js_resources=js_resources, css_resources=css_resources, **data)
    else:
        return render_template('relatorios_admin.html', is_admin=False)

@flask_app.route('/relatorios/restaurante')
def relatorios_restaurante():
    restaurante = Singleton().get_current_restaurant_flask()
    if restaurante is not None:

        js_resources = INLINE.render_js()
        css_resources = INLINE.render_css()

        # consultas para os relatórios
        media_gasta = my_db.media_gasta(restaurante.pk)
        graph1 = bk.restaurant_graph1(media_gasta)

        maior_compra = my_db.maior_compra_restaurante(restaurante.pk) # não precisa de gráfico

        maior_pedido = my_db.maior_pedido_restaurante(restaurante.pk) # não precisa de gráfico

        maior_e_menor_comissao = my_db.maior_e_menor_comissao_paga_restaurante(restaurante.pk) # não de precisa gráfico

        item_mais_pedido = my_db.item_mais_pedido(restaurante.pk) # não precisa de gráfico

        pedidos_p_status = my_db.qnts_pedidos_p_status(restaurante.pk)
        graph2 = bk.restaurant_graph2(pedidos_p_status)

        pedidos_dia_semana = my_db.pedidos_dia_semana(restaurante.pk)
        graph3 = bk.restaurant_graph3(pedidos_dia_semana)

        data = { # salva as informaçõs num dicionário para melhor organização
            'graph1': graph1,
            'maior_compra': maior_compra,
            'maior_pedido': maior_pedido,
            'maior_e_menor_comissao': maior_e_menor_comissao,
            'item_mais_pedido': item_mais_pedido,
            'graph2': graph2,
            'graph3': graph3
        }

        return render_template('relatorios_restaurante.html', is_restaurant=True,
                               js_resources=js_resources, css_resources=css_resources, **data)
    else:
        return render_template('relatorios_restaurante.html', is_restaurant=False)
