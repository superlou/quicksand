import sqlite3


class SqliteDb:
    def __init__(self, path):
        self.conn = sqlite3.connect('app.db')
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def info(self):
        print(f'SQLite version: {sqlite3.sqlite_version}')

    def close(self):
        self.conn.commit()
        self.conn.close()

    def execute(self, sql):
        return self.cursor.execute(sql)

    def create_table(self, name):
        sql = f'CREATE TABLE {name} (id INTEGER PRIAMRY KEY);'
        self.cursor.execute(sql)

    def rename_table(self, old, new):
        sql = f'ALTER TABLE {old} RENAME TO {new}'
        self.cursor.execute(sql)

    def drop_table(self, name):
        sql = f'DROP TABLE {name};'
        self.cursor.execute(sql)

    def add_column(self, table, name, datatype):
        sql = f'ALTER TABLE {table} ADD COLUMN {name} {datatype}'
        self.cursor.execute(sql)

    # todo This doesn't work on SQLite 3.22.0
    # def rename_column(self, table, old, new):
    #     sql = f'ALTER TABLE {table} RENAME {old} TO {new}'
    #     self.cursor.execute(sql)

    @property
    def table_names(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        return [result[0] for result in self.cursor.execute(sql).fetchall()]

    def get_table_info(self, name):
        return self.cursor.execute(f'PRAGMA table_info({name})').fetchall()

    @property
    def schema(self):
        return {
            'tables': [{'name': table} for table in self.table_names]
        }
