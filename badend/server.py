#!/usr/bin/python3
from flask import Flask, Response, make_response
from flask_restful import Api, Resource
import json
from .sqlite_db import SqliteDb as Db


def get_all_handler(self):
    resource = self.__class__.resource
    db = Db(self.__class__.app)

    data = []

    sql = f'SELECT * FROM {resource}'

    for record in db.execute(sql).fetchall():
        data.append(format_resource_object(record, resource)['data'])

    response = make_response({
        'data': data
    })
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def get_one_handler(self, id):
    resource = self.__class__.resource
    db = Db(self.__class__.app)
    sql = f'SELECT * FROM {resource} WHERE id={id}'
    result = db.execute(sql).fetchone()

    if result is None:
        response = make_response({
            'errors': [{
                'title': 'Resource not found',
                'detail': f'Resource "{resource}" with id "{id}" not found'
            }]
        })
        response.status_code = 404
    else:
        response = make_response(format_resource_object(result, resource))
        response.status_code = 200

    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


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


def create_app(database='app.db'):
    app = Flask(__name__)
    app.config['DATABASE'] = database

    api = Api(app)

    @app.route('/')
    def index():
        return 'Badend Server'

    for name in Db(app.config['DATABASE']).table_names:
        klass = type(f'HandlerList{name}', (Resource,), {
            'get':  get_all_handler,
            'resource': name,
            'app': app,
        })

        api.add_resource(klass, f'/api/{name}')

        klass = type(f'HandlerSingle{name}', (Resource,), {
            'get':  get_one_handler,
            'resource': name,
            'app': app,
        })

        api.add_resource(klass, f'/api/{name}/<int:id>')

    return app
