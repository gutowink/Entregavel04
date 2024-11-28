from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import LabelSet, ColumnDataSource
from bokeh.resources import INLINE
from bokeh.transform import dodge


def to_column_source(df):
    return ColumnDataSource(df)

class Bokeh:
    def __init__(self):
        self.js_resources = INLINE.render_js()
        self.css_resources = INLINE.render_css()

    def render_graph(self, fig):
        sc, dv = components(fig)
        d = dict(plot_div=dv, plot_script=sc,js_resources=self.js_resources, css_resources=self.css_resources)
        return d

    def restaurant_graph1(self, media_gasta):
        data_source = to_column_source(media_gasta)

        fig = figure(
            x_range=data_source.data['Nome'],
            title="Média Gasta por Usuário",
            x_axis_label='Usuários',
            y_axis_label='Média Gasta',
            height=450,
            tools="pan,box_zoom,reset,save",
        )

        fig.vbar(x='Nome', top='MediaGasta', width=0.5, source=data_source, color="tomato")
        labels = LabelSet(x='Nome', y='MediaGasta', text='MediaGasta', level='glyph', text_align='center', y_offset=5,
                           source=data_source)
        fig.add_layout(labels)

        return self.render_graph(fig)

    def restaurant_graph2(self, pedidos_status):
        status = ['Criado', 'Aceito', 'Saiu para entrega', 'Entregue', 'Recusado']
        counts = [
            pedidos_status['Criado'][0],
            pedidos_status['Aceito'][0],
            pedidos_status['SaiuParaEntrega'][0],
            pedidos_status['Entregue'][0],
            pedidos_status['Recusado'][0],
        ]

        source = ColumnDataSource(data=dict(status=status, count=counts))

        fig = figure(
            x_range=status,  # Eixo X com os status
            title="Quantidade de Pedidos por Status",
            x_axis_label="Status",
            y_axis_label="Quantidade",
            height=450,
            tools="pan,box_zoom,reset,save"
        )

        fig.vbar(x='status', top='count', width=0.5, source=source, color="slateblue")

        labels = LabelSet(x='status', y='count', text='count', level='glyph', text_align='center', y_offset=5,
                          source=source)
        fig.add_layout(labels)

        return self.render_graph(fig)

    def restaurant_graph3(self, pedidos_dia):
        dias_da_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        medias = [
            pedidos_dia['Segunda'][0],
            pedidos_dia['Terça'][0],
            pedidos_dia['Quarta'][0],
            pedidos_dia['Quinta'][0],
            pedidos_dia['Sexta'][0],
            pedidos_dia['Sábado'][0]
        ]

        source = ColumnDataSource(data=dict(dia=dias_da_semana, media=medias))

        fig = figure(
            x_range=dias_da_semana,
            title="Média de Pedidos por Dia da Semana",
            x_axis_label="Dia da Semana",
            y_axis_label="Média de Pedidos",
            height=450,
            tools="pan,box_zoom,reset,save"
        )

        fig.vbar(x='dia', top='media', width=0.5, source=source, color="lightgreen")

        labels = LabelSet(x='dia', y='media', text='media', level='glyph', text_align='center', y_offset=5,
                          source=source)
        fig.add_layout(labels)

        return self.render_graph(fig)

    def admin_graph1(self, clientes_unicos_data):
        data_source = to_column_source(clientes_unicos_data)

        fig = figure(
            x_range=data_source.data['Restaurante'],
            title="Clientes Únicos por Restaurante",
            x_axis_label='Restaurantes',
            y_axis_label='Clientes Únicos',
            height=450,
            tools="pan,box_zoom,reset,save",
        )

        fig.vbar(x='Restaurante', top='ClientesUnicos', width=0.5, source=data_source, color="orange")

        labels = LabelSet(x='Restaurante', y='ClientesUnicos', text='ClientesUnicos',
                          level='glyph', text_align='center', y_offset=5, source=data_source)
        fig.add_layout(labels)

        return self.render_graph(fig)

    def admin_graph2(self, ticket_medio_data):
        data_source = to_column_source(ticket_medio_data)

        fig = figure(
            x_range=data_source.data['Restaurante'],
            title="Ticket Médio por Restaurante",
            x_axis_label='Restaurantes',
            y_axis_label='Ticket Médio (R$)',
            height=450,
            tools="pan,box_zoom,reset,save",
        )

        fig.vbar(x='Restaurante', top='TicketMedio', width=0.5, source=data_source, color="turquoise")

        labels = LabelSet(x='Restaurante', y='TicketMedio', text='TicketMedio',
                          level='glyph', text_align='center', y_offset=5, source=data_source)
        fig.add_layout(labels)

        fig.xaxis.major_label_orientation = "vertical"

        return self.render_graph(fig)

    def admin_graph3(self, pedidos_restaurante):
        restaurantes = pedidos_restaurante['NomeRestaurante']
        meses = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        data = {'mes': meses}
        for idx, restaurante in enumerate(restaurantes):
            data[restaurante] = [
                pedidos_restaurante[mes][idx] for mes in meses
            ]

        source = ColumnDataSource(data=data)

        fig = figure(
            x_range=meses,
            title="Pedidos por Mês e Restaurante",
            x_axis_label="Mês",
            y_axis_label="Total de Pedidos",
            height=450,
            width=900,
            tools="pan,box_zoom,reset,save"
        )

        cores = ["mediumseagreen", "tomato", "dodgerblue", "gold", "purple"]
        largura_barra = 0.8 / len(restaurantes)

        for i, restaurante in enumerate(restaurantes):
            x_offset = -0.4 + i * largura_barra
            fig.vbar(
                x=dodge('mes', x_offset, range=fig.x_range),
                top=restaurante,
                width=largura_barra,
                source=source,
                color=cores[i % len(cores)],
                legend_label=restaurante
            )

        fig.legend.title = "Restaurantes"
        fig.legend.location = "top_left"
        fig.legend.orientation = "vertical"

        return self.render_graph(fig)

    def admin_graph4(self, insight_data):
        data_source = to_column_source(insight_data)

        fig = figure(
            x_range=data_source.data['usuario'],
            title="Top 5 Usuários por Total Gasto",
            x_axis_label="Usuários",
            y_axis_label="Total Gasto",
            height=450,
            tools="pan,box_zoom,reset,save",
        )

        fig.vbar(x='usuario', top='Total', width=0.5, source=data_source, color="orchid")

        labels = LabelSet(x='usuario', y='Total', text='Total', level='glyph', text_align='center', y_offset=5,
                          source=data_source)
        fig.add_layout(labels)

        return self.render_graph(fig)

    def admin_graph5(self, restaurantes_clientes_df):
        data = {
            'Categoria': ['Restaurantes', 'Clientes'],
            'Quantidade': [
                restaurantes_clientes_df['RestaurantesCadastrados'][0],
                restaurantes_clientes_df['ClientesCadastrados'][0]
            ]
        }
        data_source = to_column_source(data)

        fig = figure(
            x_range=data['Categoria'],
            title="Quantidade de Restaurantes x Clientes Cadastrados",
            x_axis_label='Categoria',
            y_axis_label='Quantidade',
            height=450,
            tools="pan,box_zoom,reset,save",
        )

        fig.vbar(x='Categoria', top='Quantidade', width=0.5, source=data_source, color="dodgerblue")

        labels = LabelSet(
            x='Categoria',
            y='Quantidade',
            text='Quantidade',
            level='glyph',
            text_align='center',
            y_offset=5,
            source=data_source
        )
        fig.add_layout(labels)

        return self.render_graph(fig)




