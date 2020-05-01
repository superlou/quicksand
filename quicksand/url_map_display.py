import flask
from flask import render_template


def render_url_map(url_map):
    rules = list(url_map.iter_rules())
    rules = sorted(rules, key=lambda rule: str(rule))

    methods = ['GET', 'POST', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

    rule_rows = []

    for rule in rules:
        row = [flask.escape(rule.rule)]

        for method in methods:
            if method in rule.methods:
                row.append("&#x2713;")
            else:
                row.append('')

        rule_rows.append(row)

    return render_template('url_map.html', methods=methods, rows=rule_rows)
