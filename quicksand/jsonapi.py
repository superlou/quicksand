from flask import make_response


def make_null_relationship_response():
    response = make_response({'data': None})
    response.status_code = 200
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def make_empty_relationship_response():
    response = make_response({'data': []})
    response.status_code = 200
    response.headers['Content-Type'] = 'application/vnd.api+json'
    return response


def make_jsonapi_response(data, status_code=200):
    response = make_response(data)
    response.headers['Content-Type'] = 'application/vnd.api+json'
    response.status_code = status_code
    return response
