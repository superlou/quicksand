#!/usr/bin/python3
import json
from tabulate import tabulate
from sqlite_db import SqliteDb as Db
import sys
import os.path
import server


def print_schema(db):
    tables = db.table_names
    for name in tables:
        print(name)
        info = db.get_table_info(name)
        print(tabulate(info, tablefmt='fancy_grid'))


def process_cmd(tokens, db):
    if tokens[0] == 'add':
        if '.' in tokens[1]:
            table, column = tokens[1].split('.')
            db.add_column(table, column, tokens[2])
        else:
            db.create_table(tokens[1])

    elif tokens[0] == 'drop':
        if '.' in tokens[1]:
            pass
        else:
            db.drop_table(tokens[1])

    elif tokens[0] == 'rename':
        if '.' in tokens[1]:
            pass
        else:
            db.rename_table(tokens[1], tokens[2])

    elif tokens[0] == 'schema':
        print_schema(db)

    elif tokens[0] == 'serve':
        server.run()


if __name__ == '__main__':
    db = Db('app.db')
    print(db.info())

    if not os.path.isfile('app.json'):
        open('app.json', 'a').close()

    app = json.load(open('app.json'))

    args = sys.argv

    if len(args) > 1:
        process_cmd(args[1:], db)

    app['schema'] = db.schema
    db.close()
    json.dump(app, open('app.json', 'w'), indent=4, sort_keys=True)
