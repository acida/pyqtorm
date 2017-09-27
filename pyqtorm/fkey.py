# -*-  coding: Utf-8 -*-t
from field import Field


class FKey(Field):

    def __init__(self, _db_object, _field, _caption, _foreign_class):
        Field.__init__(_db_object, _field, _caption)
        self.foreign_class = _foreign_class
