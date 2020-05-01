import inflect


def infer_relationships(db):
    resources = {table: [] for table in db.table_names}

    p = inflect.engine()

    for resource in db.table_names:
        for column in db.table_columns(resource):
            if column.endswith('_id'):
                belongs_to = column[:-3]
                belongs_to_resource = p.plural(belongs_to)
                # resources[resource].append(('belongs_to', belongs_to))
                # resources[belongs_to_resouce].append(('has_many', resource))
                resources[resource].append(BelongsTo(resource, belongs_to))
                resources[belongs_to_resource].append(HasMany(belongs_to_resource, resource))


    return resources


class BelongsTo:
    def __init__(self, resource, relationship_name):
        p = inflect.engine()
        self.name = relationship_name
        self.related_resource = p.plural(relationship_name)
        self.lookup_table = p.plural(relationship_name)
        self.lookup_id = 'id'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.name == other.name and \
               self.lookup_table == other.lookup_table and \
               self.lookup_id == other.lookup_id

    def __repr__(self):
        return f'<BelongsTo name={self.name}, lookup_table={self.lookup_table}, lookup_id={self.lookup_id}>'


class HasMany:
    def __init__(self, resource, relationship_name):
        p = inflect.engine()
        self.name = relationship_name
        self.related_resource = relationship_name
        self.lookup_table = relationship_name
        self.lookup_id = p.singular_noun(resource) + '_id'

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return NotImplemented

        return self.name == other.name and \
               self.lookup_table == other.lookup_table and \
               self.lookup_id == other.lookup_id

    def __repr__(self):
        return f'<HasMany name={self.name}, lookup_table={self.lookup_table}, lookup_id={self.lookup_id}>'
