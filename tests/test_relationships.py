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


def test_relationships_inference(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    app = create_app(db_path)
    assert app.config['RELATIONSHIPS'] == {
        'articles': [
            ('belongs_to', 'author')
        ],
        'authors': [
            ('has_many', 'articles')
        ]
    }


def test_get_belongs_to(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()

    response = client.get('/api/articles/1')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.get_json()['data']['relationships'] == {
        'author': {
            'links': {
                'related': 'http://localhost/api/articles/1/author'
            }
        }
    }

    response = client.get('api/articles/1/author')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.get_json() == {
        'data': {
            'type': 'authors',
            'id': 1,
            'attributes': {
                'name': 'Author 1',
            },
            'links': {
                'self': 'http://localhost/api/authors/1'
            },
            'relationships': {
                'articles': {
                    'links': {
                        'related': 'http://localhost/api/authors/1/articles'
                    }
                }
            }
        }
    }

    response = client.get('api/articles/2/author')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.get_json() == {
        'data': None
    }


def test_get_has_many(db_path):
    Db(db_path).execute_script('tests/sql/basic.sql')
    client = create_app(db_path).test_client()

    response = client.get('/api/authors/1')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.get_json()['data']['relationships'] == {
        'articles': {
            'links': {
                'related': 'http://localhost/api/authors/1/articles'
            }
        }
    }

    response = client.get('api/authors/1/articles')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.get_json() == {
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
                },
                'relationships': {
                    'author': {
                        'links': {
                            'related': 'http://localhost/api/articles/1/author'
                        }
                    }
                }
            }
        ]
    }
