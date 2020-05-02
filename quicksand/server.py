#!/usr/bin/python3
import flask
from flask import Flask, Response, request
from flask_restful import Api, Resource
import json
import inflect
from .sqlite_db import SqliteDb as Db
from .relationships import infer_relationships
from .url_map_display import render_url_map
from .relationships import BelongsTo, HasMany
from .jsonapi import make_null_relationship_response, make_empty_relationship_response
from .jsonapi import make_jsonapi_response


def fetch_resources(self):
    resource = self.__class__.resource
    relationships = self.__class__.relationships
    db = Db(self.__class__.app.config['DATABASE'])
    records = db.find_all(resource)
    obj = format_resource_object(records, resource, request.url_root, relationships)
    return make_jsonapi_response(obj)


def fetch_resource(self, id):
    resource = self.__class__.resource
    relationships = self.__class__.relationships
    db = Db(self.__class__.app.config['DATABASE'])
    result = db.find_by_id(resource, id)

    if result is None:
        return response_not_found(resource, id)

    obj = format_resource_object(result, resource, request.url_root, relationships)
    return make_jsonapi_response(obj)


def response_not_found(resource, id):
    obj = {
        'errors': [{
            'title': 'Resource not found',
            'detail': f'Resource "{resource}" with id "{id}" not found'
        }]
    }
    return make_jsonapi_response(obj, 404)


def create_resource(self):
    resource = self.__class__.resource
    relationships = self.__class__.relationships
    db = Db(self.__class__.app.config['DATABASE'])

    request_data = request.get_json()['data']
    record_data = request_data['attributes']

    # Modify the created resource's table
    belongs_to_rels = [r for r in relationships if isinstance(r, BelongsTo)]
    for relationship in belongs_to_rels:
        try:
            rel_data = request_data['relationships'][relationship.name]['data']
            rel_resource_type = rel_data['type']
            rel_id = rel_data['id']
        except KeyError:
            continue

        if rel_resource_type != relationship.related_resource:
            continue

        record_data[relationship.name + '_id'] = rel_id

    id = db.insert_into(resource, record_data)

    # Modify fields in related tables
    has_many_rels = [r for r in relationships if isinstance(r, HasMany)]
    for relationship in has_many_rels:
        try:
            rel_datas = request_data['relationships'][relationship.name]['data']
            for rel_data in rel_datas:
                db.update_by_id(relationship.lookup_table, rel_data['id'], {
                    relationship.lookup_id: id
                })
        except KeyError:
            continue


    result = db.find_by_id(resource, id)
    obj = format_resource_object(result, resource, request.url_root, relationships)
    return make_jsonapi_response(obj, 201)


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
    relationship = self.__class__.relationship
    related_resource = relationship.related_resource
    db = Db(self.__class__.app.config['DATABASE'])

    if isinstance(relationship, BelongsTo):
        relationship_column = relationship.name + '_id'
        related_id = db.find_by_id(resource, id)[relationship_column]
        result = db.find_by_id(relationship.lookup_table, related_id)

        if result is None:
            return make_null_relationship_response()

    elif isinstance(relationship, HasMany):
        result = db.find_by_field(related_resource, relationship.lookup_id, id)

        if len(result) == 0:
            return make_empty_relationship_response()

    relationships = self.__class__.app.config['RELATIONSHIPS'][related_resource]
    obj = format_resource_object(result, related_resource, request.url_root, relationships)
    return make_jsonapi_response(obj)


def format_resource_object(record, resource, url_root, relationships):
    """ Formats a single or list of records into a resource object """
    if isinstance(record, list):
        records = record
        data = [format_resource_object(record, resource, url_root,
                                       relationships)['data']
                for record in records]
        return {'data': data}

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
        id = record['id']
        data['relationships'] = {
            rel.name: {
                'links': {
                    'related': f'{url_root}api/{resource}/{id}/{rel.name}'
                }
            }
            for rel in relationships
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
        return render_url_map(app.url_map)

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

        for relationship in app.config['RELATIONSHIPS'][name]:
            klass = type(f'HandlerSingle{name}_{relationship.name}', (Resource,), {
                'get':  fetch_resource_relationship,
                'resource': name,
                'app': app,
                'relationships': app.config['RELATIONSHIPS'][name],
                'relationship': relationship,
            })
            api.add_resource(klass, f'/api/{name}/<int:id>/{relationship.name}')

    return app
