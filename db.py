import sqlite3
from os.path import isfile
from __init__ import config

class Session():
    def __init__(self):
        """
        Connects to the database, creating a new one if one does not exist
        """
        if not isfile(config['database_path']):
            with open(config['database_path'], 'w') as file:
                pass

        self.connection = sqlite3.connect(config['database_path'])
        self.cursor = self.connection.cursor()

        self.cursor.execute("""CREATE TABLE IF NOT EXISTS passwords (ID INT IDENTITY(1,1) NOT NULL PRIMARY KEY,association,phrase,padding,iv NOT NULL UNIQUE)""")

    def __enter__ (self):
        return self

    def __exit__ (self, exc_type, exc_value, traceback):
        self.connection.commit()
        self.connection.close()
    
    def create_row(self, phrase, iv, padding=0, association=None):
        """
        Creates a new row with given passphrase
        """
        if not association:
            association = 'Other'
        self.cursor.execute("""SELECT association FROM passwords WHERE association = 'MAIN'""")
        if association == 'MAIN' and self.cursor.fetchone():
            return {'error': 'Cannot create a row with association "MAIN"'}
        self.cursor.execute("""SELECT ID, MAX(ID) FROM passwords""")
        id = self.cursor.fetchone()
        id = 0 if id[0] == None else int(id[0]) + 1
        self.cursor.execute("""INSERT INTO passwords VALUES({id},'{association}','{phrase}','{padding}','{iv}')""".format(id=id,association=association, phrase=phrase, 
        padding=padding, iv=iv))

    def get_table(self):
        """
        Returns list of every row in the table
        """
        self.cursor.execute('SELECT * from passwords')
        return self.cursor.fetchall()

    def delete_table(self):
        """
        Removes all rows from the table
        """
        self.cursor.execute('DELETE from passwords')
    
    def delete_row(self, id=0):
        """
        Deletes a row based on id
        """
        self.cursor.execute("""SELECT association FROM passwords WHERE ID = {id}""".format(id=id))
        result = self.cursor.fetchone()
        if result and result[0] == 'MAIN':
            return {'error': 'Cannot delete row {}'.format(id)}
        
        self.cursor.execute("""DELETE FROM passwords WHERE ID = {id}""".format(id=id))

    def filter(self, associations=None):
        """
        Filters the table by associations
        """   
        sql_query = """SELECT * from passwords WHERE association != 'MAIN'"""
        if associations:
            for association in associations:
                if not association == 'MAIN':
                    sql_query += """ OR association = '{}'""".format(association)

        self.cursor.execute(sql_query)
        return self.cursor.fetchall()

    def get_main(self):
        """
        Returns the row with MAIN association
        """
        self.cursor.execute("""SELECT * from passwords WHERE association = 'MAIN'""")
        return self.cursor.fetchone()

    def raw(self, query):
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception:
            pass

    def get_iv_list(self):
        self.cursor.execute("""SELECT iv FROM passwords""")
        return self.cursor.fetchall()
