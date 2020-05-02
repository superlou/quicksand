import os
import tempfile
import pytest
from quicksand import create_app, Db, BelongsTo, HasMany


@pytest.fixture
def db_path():
    db_fd, db_path = tempfile.mkstemp()
    yield db_path
    os.close(db_fd)
    os.unlink(db_path)


def test_relationship_classes():
    belongsTo = BelongsTo('articles', 'author')
    assert belongsTo.name == 'author'
    assert belongsTo.related_resource == 'authors'
    assert belongsTo.lookup_table == 'authors'
    assert belongsTo.lookup_id == 'id'

    hasMany = HasMany('authors', 'articles')
    assert hasMany.name == 'articles'
    assert hasMany.related_resource == 'articles'
    assert hasMany.lookup_table == 'articles'
    assert hasMany.lookup_id == 'author_id'


def test_relationships_inference(db_path):
    Db(db_path).execute_script('tests/sql/relationships.sql')
    app = create_app(db_path)

    assert app.config['RELATIONSHIPS']['articles'] == [
        BelongsTo('articles', 'author')
    ]

    assert app.config['RELATIONSHIPS']['authors'] == [
        HasMany('authors', 'articles')
    ]


def test_get_belongs_to(db_path):
    Db(db_path).execute_script('tests/sql/relationships.sql')
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
    Db(db_path).execute_script('tests/sql/relationships.sql')
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


def test_create_resource_with_relationship_belongs_to(db_path):
    Db(db_path).execute_script('tests/sql/relationships.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 2

    response = client.post('/api/articles', json={
        'data': {
            'type': 'articles',
            'attributes': {
                'title': 'Article 3',
                'body': 'Body 3',
            },
            'relationships': {
                'author': {
                    'data': {'type': 'authors', 'id': 1}
                }
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
            },
            'relationships': {
                'author': {
                    'links': {
                        'related': 'http://localhost/api/articles/3/author'
                    }
                }
            }
        }
    }

    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 3

    response = client.get('http://localhost/api/articles/3/author')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 200
    assert response.get_json(force=True)['data']['type'] == 'authors'
    assert response.get_json(force=True)['data']['id'] == 1


def test_create_resource_with_relationship_has_many(db_path):
    Db(db_path).execute_script('tests/sql/relationships.sql')
    client = create_app(db_path).test_client()
    response = client.get('/api/authors')
    assert len(response.get_json(force=True)['data']) == 1

    response = client.post('/api/authors', json={
        'data': {
            'type': 'authors',
            'attributes': {
                'name': 'Author 2',
            },
            'relationships': {
                'articles': {
                    'data': [
                        {'type': 'articles', 'id': 1},
                        {'type': 'articles', 'id': 2},
                    ]
                }
            }
        }
    })

    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 201
    assert response.get_json(force=True) == {
        'data': {
            'type': 'authors',
            'id': 2,
            'attributes': {
                'name': 'Author 2',
            },
            'links': {
                'self': 'http://localhost/api/authors/2'
            },
            'relationships': {
                'articles': {
                    'links': {
                        'related': 'http://localhost/api/authors/2/articles'
                    }
                }
            }
        }
    }

    response = client.get('/api/articles')
    assert len(response.get_json(force=True)['data']) == 2

    # Make sure author sees both articles
    response = client.get('http://localhost/api/authors/2/articles')
    assert response.headers['Content-Type'] == 'application/vnd.api+json'
    assert response.status_code == 200
    assert len(response.get_json(force=True)['data']) == 2
