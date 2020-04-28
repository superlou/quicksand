#!/usr/bin/python3
from flask import Flask
from flask_restful import Api, Resource
import json
from sqlite_db import SqliteDb as Db


app = Flask(__name__)


@app.route('/')
def index():
    return 'Badend Server'


def get_all_handler(self):
    resource = self.__class__.resource
    db = Db('app.db')

    data = []

    sql = f'SELECT * FROM {resource}'

    for record in db.execute(sql).fetchall():
        data.append(format_resource_object(record, resource))

    return {
        'data': data
    }


def get_one_handler(self, id):
    resource = self.__class__.resource
    db = Db('app.db')
    sql = f'SELECT * FROM {resource} WHERE id={id}'
    result = db.execute(sql).fetchone()

    if result is None:
        return {
            'errors': [{
                'title': 'Resource not found',
                'detail': f'Resource "{resource}" with id "{id}" not found'
            }]
        }, 404

    return format_resource_object(result, resource)


def find_related(resource, id, db):
    foreign_key_column = resource + '_id'
    tables = db.table_names

    related = []

    for table in tables:
        for row in db.get_table_info(table):
            print(row['name'])
            if row['name'] == foreign_key_column:
                related.append(table)

    return related


def format_resource_object(record, resource):
    data = {
        'type': resource,
        'id': record['id']
    }

    data['attributes'] = {}

    for key in [key for key in record.keys() if key != 'id']:
        data['attributes'][key] = record[key]

    return {
        'data': data
    }


def run():
    api = Api(app)
    db = Db('app.db')

    for name in db.table_names:
        klass = type(f'HandlerList{name}', (Resource,), {
            'get':  get_all_handler,
            'resource': name,
        })

        api.add_resource(klass, f'/api/{name}')

        klass = type(f'HandlerSingle{name}', (Resource,), {
            'get':  get_one_handler,
            'resource': name,
        })

        api.add_resource(klass, f'/api/{name}/<int:id>')

    app.run(debug=True)


if __name__ == '__main__':
    run()
