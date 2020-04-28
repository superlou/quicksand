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

    def execute_script(self, filename):
        with open(filename) as script_file:
            self.cursor.executescript(script_file.read())

    @property
    def table_names(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        return [result[0] for result in self.cursor.execute(sql).fetchall()]

    def get_table_info(self, name):
        return self.cursor.execute(f'PRAGMA table_info({name})').fetchall()
