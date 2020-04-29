import os
import tempfile

import pytest

from badend import create_app, Db


@pytest.fixture
def db_path():
    db_fd, db_path = tempfile.mkstemp()
    yield db_path
    os.close(db_fd)
    os.unlink(db_path)


def test_empty_db(db_path):
    client = create_app(db_path).test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b'Badend Server'


def test_get_one_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/parts/1')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 200
    assert response.get_json() == {
        'data': {
            'type': 'parts',
            'id': 1,
            'attributes': {
                'desc': 'some description',
                'name': 'part1',
            },
            'links': {
                'self': 'http://localhost/api/parts/1'
            }
        }
    }

    response = client.get('/api/parts/2')
    assert response.status_code == 200
    assert response.get_json() == {
        'data': {
            'type': 'parts',
            'id': 2,
            'attributes': {
                'desc': 'another description',
                'name': 'part2',
            },
            'links': {
                'self': 'http://localhost/api/parts/2'
            }
        }
    }


def test_get_one_not_found(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/parts/3')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 404
    assert response.get_json() == {
        'errors': [{
            'title': 'Resource not found',
            'detail': 'Resource "parts" with id "3" not found'
        }]
    }


def test_get_all(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/parts')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 200
    assert response.get_json(force=True) == {
        'data': [
            {
                'type': 'parts',
                'id': 1,
                'attributes': {
                    'desc': 'some description',
                    'name': 'part1',
                },
                'links': {
                    'self': 'http://localhost/api/parts/1'
                }
            },
            {
                'type': 'parts',
                'id': 2,
                'attributes': {
                    'desc': 'another description',
                    'name': 'part2',
                },
                'links': {
                    'self': 'http://localhost/api/parts/2'
                }
            },

        ]
    }


def test_create_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/parts')
    assert len(response.get_json(force=True)['data']) == 2

    response = client.post('/api/parts', json={
        'data': {
            'type': 'parts',
            'attributes': {
                'name': 'Just',
                'desc': 'Created',
            }
        }
    })

    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 201
    assert response.get_json(force=True) == {
        'data': {
            'type': 'parts',
            'id': 3,
            'attributes': {
                'name': 'Just',
                'desc': 'Created',
            },
            'links': {
                'self': 'http://localhost/api/parts/3'
            }
        }
    }

    response = client.get('/api/parts')
    assert len(response.get_json(force=True)['data']) == 3


def test_delete_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/parts')
    assert len(response.get_json(force=True)['data']) == 2

    response = client.delete('/api/parts/1')
    assert response.status_code == 204

    response = client.get('/api/parts')
    assert len(response.get_json(force=True)['data']) == 1
    assert response.get_json(force=True)['data'][0]['id'] == 2
