import sqlite3


class SqliteDb:
    def __init__(self, path):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def info(self):
        print(f'SQLite version: {sqlite3.sqlite_version}')

    def commit(self):
        self.conn.commit()

    def close(self):
        self.commit()
        self.conn.close()

    def execute(self, sql):
        return self.cursor.execute(sql)

    def execute_script(self, filename):
        with open(filename) as script_file:
            self.cursor.executescript(script_file.read())

    def insert_into(self, table, data):
        columns = ','.join(data.keys())
        values = tuple(data.values())
        templates = ','.join('?' * len(values))

        sql = f'INSERT INTO {table} ({columns}) VALUES ({templates});'
        self.cursor.execute(sql, values)
        self.commit()

        # lastrowid is the id of the last row inserted into for that cursor
        # only. Another cursor will have a different lastrowid.
        return self.cursor.lastrowid

    @property
    def table_names(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        return [result[0] for result in self.cursor.execute(sql).fetchall()]

    def get_table_info(self, name):
        return self.cursor.execute(f'PRAGMA table_info({name})').fetchall()