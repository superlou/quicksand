import os
import tempfile

import pytest

from quicksand import create_app, Db


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


def test_get_one_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/articles/1')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 200
    assert response.get_json() == {
        'data': {
            'type': 'articles',
            'id': 1,
            'attributes': {
                'title': 'Article 1',
                'body': 'Body 1',
            },
            'links': {
                'self': 'http://localhost/api/articles/1'
            }
        }
    }

    response = client.get('/api/articles/2')
    assert response.status_code == 200
    assert response.get_json() == {
        'data': {
            'type': 'articles',
            'id': 2,
            'attributes': {
                'title': 'Article 2',
                'body': 'Body 2',
            },
            'links': {
                'self': 'http://localhost/api/articles/2'
            }
        }
    }


def test_get_one_not_found(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/articles/3')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 404
    assert response.get_json() == {
        'errors': [{
            'title': 'Resource not found',
            'detail': 'Resource "articles" with id "3" not found'
        }]
    }


def test_get_all(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/articles')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 200
    assert response.get_json(force=True) == {
        'data': [
            {
                'type': 'articles',
                'id': 1,
                'attributes': {
                    'title': 'Article 1',
                    'body': 'Body 1',
                },
                'links': {
                    'self': 'http://localhost/api/articles/1'
                }
            },
            {
                'type': 'articles',
                'id': 2,
                'attributes': {
                    'title': 'Article 2',
                    'body': 'Body 2',
                },
                'links': {
                    'self': 'http://localhost/api/articles/2'
                }
            },
        ]
    }


def test_create_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 2

    response = client.post('/api/articles', json={
        'data': {
            'type': 'articles',
            'attributes': {
                'title': 'Article 3',
                'body': 'Body 3',
            }
        }
    })

    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 201
    assert response.get_json(force=True) == {
        'data': {
            'type': 'articles',
            'id': 3,
            'attributes': {
                'title': 'Article 3',
                'body': 'Body 3',
            },
            'links': {
                'self': 'http://localhost/api/articles/3'
            }
        }
    }

    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 3


def test_delete_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 2

    response = client.delete('/api/articles/1')
    assert response.status_code == 204

    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 1
    assert response.get_json(force=True)['data'][0]['id'] == 2


def test_update_resource(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()

    response = client.patch('/api/articles/1', json={
        'data': {
            'type': 'articles',
            'id': 1,
            'attributes': {
                'body': 'changed',
            }
        }
    })

    assert response.status_code == 204

    # Make sure that we've changed only the desired record
    response = client.get('/api/articles/1')
    data = response.get_json(force=True)['data']
    assert data['attributes']['title'] == 'Article 1'
    assert data['attributes']['body'] == 'changed'

    response = client.get('/api/articles/2')
    data = response.get_json(force=True)['data']
    assert data['attributes']['title'] == 'Article 2'
    assert data['attributes']['body'] == 'Body 2'
