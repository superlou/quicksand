import flask


def format_url_map(url_map):
    rules = list(url_map.iter_rules())
    rules = sorted(rules, key=lambda rule: str(rule))

    html = '<table border=1>'

    methods = ['GET', 'POST', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS']

    html += '<tr><td></td>'
    for method in methods:
        html += f'<td>{method}</td>'

    html += '</tr>'

    for rule in rules:
        path = flask.escape(rule.rule)

        html += "<tr>"
        # methods = ', '.join(list(rule.methods))
        html += f'<td>{path}</td>'

        for method in methods:
            html += "<td>"
            if method in rule.methods:
                html += "&#x2713;"

            html += "</td>"

        html += "</tr>"

    html += '</table>'

    return html
