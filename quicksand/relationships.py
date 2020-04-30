import inflect


def infer_relationships(db):
    resources = {table: [] for table in db.table_names}

    p = inflect.engine()

    for resource in db.table_names:
        for column in db.table_columns(resource):
            if column.endswith('_id'):
                belongs_to = column[:-3]
                belongs_to_resouce = p.plural(belongs_to)
                resources[resource].append(('belongs_to', belongs_to))
                resources[belongs_to_resouce].append(('has_many', resource))


    return resources
