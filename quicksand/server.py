#!/usr/bin/python3
import flask
from flask import Flask, Response, make_response, request
from flask_restful import Api, Resource
import json
from .sqlite_db import SqliteDb as Db


def fetch_resources(self):
    resource = self.__class__.resource
    db = Db(self.__class__.app.config['DATABASE'])

    data = [format_resource_object(record, resource, request.url_root)['data']
            for record in db.find_all(resource)]

    response = make_response({
        'data': data
    })
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def fetch_resource(self, id):
    resource = self.__class__.resource
    db = Db(self.__class__.app.config['DATABASE'])
    result = db.find_by_id(resource, id)

    if result is None:
        response = make_response({
            'errors': [{
                'title': 'Resource not found',
                'detail': f'Resource "{resource}" with id "{id}" not found'
            }]
        })
        response.status_code = 404
    else:
        response = make_response(format_resource_object(result, resource, request.url_root))
        response.status_code = 200

    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def create_resource(self):
    resource = self.__class__.resource
    db = Db(self.__class__.app.config['DATABASE'])
    id = db.insert_into(resource, request.get_json()['data']['attributes'])

    result = db.find_by_id(resource, id)
    response = make_response(format_resource_object(result, resource, request.url_root))
    response.status_code = 201
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def delete_resource(self, id):
    resource = self.__class__.resource
    db = Db(self.__class__.app.config['DATABASE'])
    db.delete_by_id(resource, id)
    return None, 204


def update_resource(self, id):
    resource = self.__class__.resource
    db = Db(self.__class__.app.config['DATABASE'])
    db.update_by_id(resource, id, request.get_json()['data']['attributes'])
    return None, 204


def find_related(resource, id, db):
    foreign_key_column = resource + '_id'
    tables = db.table_names

    related = []

    for table in tables:
        for row in db.get_table_info(table):
            if row['name'] == foreign_key_column:
                related.append(table)

    return related


def format_resource_object(record, resource, url_root):
    data = {
        'type': resource,
        'id': record['id']
    }

    data['attributes'] = {}

    for key in [key for key in record.keys() if key != 'id']:
        data['attributes'][key] = record[key]

    data['links'] = {
        'self': f'{url_root}api/{resource}/{record["id"]}'
    }

    return {
        'data': data
    }


def format_url_map(url_map):
    rules = list(url_map.iter_rules())
    rules = sorted(rules, key=lambda rule: str(rule))

    html = '<ul>'

    for rule in rules:
        methods = ', '.join(list(rule.methods))
        path = flask.escape(rule.rule)
        html += f'<li>{path} - {methods}</li>'

    html += '</ul>'

    return html


def create_app(database='app.db'):
    app = Flask(__name__)
    app.config['DATABASE'] = database

    api = Api(app)

    @app.route('/')
    def index():
        return '<h1>Quicksand Server</h1>\n' + format_url_map(app.url_map)

    for name in Db(app.config['DATABASE']).table_names:
        klass = type(f'HandlerList{name}', (Resource,), {
            'get': fetch_resources,
            'post': create_resource,
            'resource': name,
            'app': app,
        })

        api.add_resource(klass, f'/api/{name}')

        klass = type(f'HandlerSingle{name}', (Resource,), {
            'get':  fetch_resource,
            'delete': delete_resource,
            'patch': update_resource,
            'resource': name,
            'app': app,
        })

        api.add_resource(klass, f'/api/{name}/<int:id>')

    return app
