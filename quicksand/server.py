#!/usr/bin/python3
import flask
from flask import Flask, Response, make_response, request
from flask_restful import Api, Resource
import json
import inflect
from .sqlite_db import SqliteDb as Db
from .relationships import infer_relationships
from .url_map_display import format_url_map


def fetch_resources(self):
    resource = self.__class__.resource
    relationships = self.__class__.relationships
    db = Db(self.__class__.app.config['DATABASE'])

    data = [format_resource_object(record, resource, request.url_root, relationships)['data']
            for record in db.find_all(resource)]

    response = make_response({
        'data': data
    })
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def fetch_resource(self, id):
    resource = self.__class__.resource
    relationships = self.__class__.relationships
    db = Db(self.__class__.app.config['DATABASE'])
    result = db.find_by_id(resource, id)

    if result is None:
        return response_not_found(resource, id)

    response = make_response(format_resource_object(result, resource, request.url_root, relationships))
    response.status_code = 200
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def response_not_found(resource, id):
    response = make_response({
        'errors': [{
            'title': 'Resource not found',
            'detail': f'Resource "{resource}" with id "{id}" not found'
        }]
    })
    response.status_code = 404
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def create_resource(self):
    resource = self.__class__.resource
    relationships = self.__class__.relationships
    db = Db(self.__class__.app.config['DATABASE'])
    id = db.insert_into(resource, request.get_json()['data']['attributes'])

    result = db.find_by_id(resource, id)
    response = make_response(format_resource_object(result, resource, request.url_root, relationships))
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


def fetch_resource_relationship(self, id):
    resource = self.__class__.resource
    relationship_type = self.__class__.relationship_type
    relationship_name = self.__class__.relationship_name
    db = Db(self.__class__.app.config['DATABASE'])

    ie = inflect.engine()

    if relationship_type == 'belongs_to':
        related_resource = ie.plural(relationship_name)
        related_id = db.find_by_id(resource, id)[relationship_name + '_id']

    result = db.find_by_id(related_resource, related_id)

    if result is None:
        response = make_response({'data': None})
        response.status_code = 200
        response.headers['Content-Type'] = 'application/vnd.api+json'
        return response

    relationships = self.__class__.app.config['RELATIONSHIPS'][related_resource]
    response = make_response(format_resource_object(result, related_resource, request.url_root, relationships))
    response.status_code = 200
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def format_resource_object(record, resource, url_root, relationships):
    data = {
        'type': resource,
        'id': record['id']
    }

    data['attributes'] = {}

    for key in [key for key in record.keys() if key != 'id' and not key.endswith('_id')]:
        data['attributes'][key] = record[key]

    data['links'] = {
        'self': f'{url_root}api/{resource}/{record["id"]}'
    }

    if len(relationships) > 0:
        data['relationships'] = {
            name: {
                'links': {
                    'related': f'{url_root}api/{resource}/{record["id"]}/{name}'
                }
            }
            for relationship_type, name in relationships
        }

    return {
        'data': data
    }


def create_app(database='app.db'):
    app = Flask(__name__)
    app.config['DATABASE'] = database
    app.config['RELATIONSHIPS'] = infer_relationships(Db(database))

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
            'relationships': app.config['RELATIONSHIPS'][name],
        })

        api.add_resource(klass, f'/api/{name}')

        klass = type(f'HandlerSingle{name}', (Resource,), {
            'get':  fetch_resource,
            'delete': delete_resource,
            'patch': update_resource,
            'resource': name,
            'app': app,
            'relationships': app.config['RELATIONSHIPS'][name],
        })

        api.add_resource(klass, f'/api/{name}/<int:id>')

        for relationship_type, relationship_name in app.config['RELATIONSHIPS'][name]:
            klass = type(f'HandlerSingle{name}_{relationship_name}', (Resource,), {
                'get':  fetch_resource_relationship,
                'resource': name,
                'app': app,
                'relationships': app.config['RELATIONSHIPS'][name],
                'relationship_type': relationship_type,
                'relationship_name': relationship_name,
            })
            api.add_resource(klass, f'/api/{name}/<int:id>/{relationship_name}')

    return app
