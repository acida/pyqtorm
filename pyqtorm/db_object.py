# -*-  coding: Utf-8 -*-t
from PyQt4.QtCore import QObject, SIGNAL
from field import Field
from fkey import FKey





class DbObject(QObject):
    table = None

    signal_data_changed = SIGNAL("data_changed(int)")

    class States(object):
        state_transient = 0
        state_pending = 1
        state_persistent = 2
        state_deleted = 3
        state_detached = 4

    def __init__(self, _parent=None):
        QObject.__init__(self,_parent)
        self.values = []
        self.state = DbObject.States.state_transient
        self.children = []
        self.fields = []
        self.fields = []
        self.headers = []
        self.foreign_objects = {}
        self.parent = None
        self.column_count = 0
        self.id = Field(self, "id", u"Уникальный идентификатор")

    def get_column_count(self):
        return self.column_count

    def get_field_name(self, _index):
        return self.fields[_index]

    def get_field_headers(self, _index):
        return self.headers[_index]

    def data(self, index = None, field = None):
        if field is not None:
            index = self.fields.index(field)
        val = None
        if index < len(self.values) and index < len(self.fields):
            if isinstance(self.fields[index],FKey):
                val = unicode(self.foreign_objects[index])
            else:
                val = self.values[index]
        return val

    def set_data(self, field=None, index=None, data=None):
        if field is not None:
            index = self.fields.index(field)
            self.values[index] = data
            self.emit(self.signal_data_changed,index)
        if index is not None:
            self.values[index] = data
            self.emit(self.signal_data_changed, index)

    def current_state(self):
        return self.state

    def add_field(self,_field):
        assert issubclass(_field.__class__, Field)
        if not self.fields.__contains__(_field):
            self.column_count += 1
            self.fields.append(_field.field)
            self.headers.append(_field.header)

        _field.index = self.fields.index(_field.field)
        self.values.append(None)
        if isinstance(_field, FKey):
            self.foreign_objects[_field.index] = _field.foreign_class()

    def __setattr__(self, name, value):
        if self.__dict__.__contains__(name):
            if isinstance(self.__dict__[name], Field):
                index = self.__dict__[name].index
                self.set_data(index=index, data=value)
            else:
                self.__dict__[name] = value
        else:
            self.__dict__[name] = value

    def __set_current_state(self, state):
        self.state = state

    def __set_id(self, value):
        self.id = value

    def set_parent(self, _parent):
        self.parent = _parent

    def get_parent(self):
        return self.parent

    def __add_child(self, _child):
        self.children.append(_child)

    def get_children(self):
        return self.children
