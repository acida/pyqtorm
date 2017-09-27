# -*-  coding: Utf-8 -*-t


class Field(object):

    def __init__(self, _db_object, _field, _caption):
        self.db_object = _db_object
        self.field = _field
        self.header = _caption
        self.index = 0
        self.db_object.add_field(self)

    def __repr__(self):
        return unicode(self.db_object.data(field=self.field))

    def __radd__(self, other):
        return other + self.db_object.data(field=self.field)
