from app.app import App
from database.db import DB
from utils.utils import Utils
from utils.insert_tables import Inserts

if __name__ == '__main__':
    Utils.clear_screen()
    db_name = 'GulaExpress.db'
    db = DB(db_name)
    connection = db.get_connection()

    if not db.get_restaurants_catalog():  # se as tabelas estão vazias
        inserts = input('Precisa de inserts? (s/n): ').lower()
        if inserts == 's':
            Inserts.insert_tables(connection)  # inserts para testes de funcionalidade
            print('\nIniciando como inserts.\n')
        else:
            print('\nIniciando sem inserts.\n')

    app = App(db)
    app.start_app()
