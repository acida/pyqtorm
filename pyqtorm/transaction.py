# -*-  coding: Utf-8 -*-t
from PyQt4.QtCore import QVariant
from PyQt4.QtSql import QSqlQuery
from db_object import DbObject


class Transaction(object):

    def __init__(self, _db, _service):
        self.db = _db
        self.sql = QSqlQuery()
        self.service = _service
        self.engine = _service.get_engine()
        self.where = ""
        self.climit = None
        self.coffset = None
        self.corderby = None
        self.corder = None
        self.objects_pending = []
        self.objects_deleted = []
        self.objects_new = []
        if not self.db.isOpen():
            if self.db.open():
                self.db.transaction()
                self.sql = QSqlQuery(self.db)

    def __del__(self):
        self.db.close()

    def get_objects_pending(self):
        return self.objects_pending

    def get_objects_deleted(self):
        return self.objects_deleted

    def get_objects_new(self):
        return self.objects_new

    def filter(self, _where):
        self.where = _where
        return self

    def limit(self, _cnt):
        self.climit = _cnt
        return self

    def offset(self, _cnt):
        self.coffset = _cnt
        return self

    def orderby(self, _field, _order=u"ASC"):
        self.corderby = _field
        self.corder = _order
        return self

    def one(self, _obj):
        assert issubclass(_obj.__class__, DbObject)
        query = self.engine.select(_obj.__class__, self.where, None, None, 1)
        res = self.sql.exec_(query)
        if res:
            self.sql.next()
            self.__load_result_to_obj(_obj)
        else:
            print self.sql.lastError().text(),query
        self.filter(None)
        return res

    def all(self, _cls, _parent=None, _parent_slot=None):
        assert issubclass(_cls,DbObject)
        res = []
        query = self.engine.select(_cls,self.where, self.corderby, self.corder, self.climit, self.coffset)
        ok = self.sql.exec_(query)
        if ok:
            while self.sql.next():
                _obj = _cls()
                self.__load_result_to_obj(_obj)
                if _parent is not None:
                    _obj.setParent(_parent)
                    if _parent_slot is not None:
                        _obj.connect(_obj, _obj.signal_data_changed, _parent_slot)
                res.append(_obj)
        self.filter(None)
        self.limit(None)
        self.offset(None)
        self.orderby(None,None)
        return res

    def add(self, _obj):
        assert issubclass(_obj.__class__, DbObject)
        query = self.engine.insert(_obj)
        self.sql.prepare(query)
        self.__bind_vals(_obj)
        res = self.sql.exec_()
        if res:
            _obj.state = DbObject.States.state_pending
            _id = self.sql.lastInsertId().toULongLong()[0]
            _obj.id = QVariant(_id)
            self.objects_new.append(_obj)
        return res

    def update(self, _obj):
        assert issubclass(_obj.__class__, DbObject)
        query = self.engine.update(_obj)
        self.sql.prepare(query)
        self.__bind_vals(_obj)
        res = self.sql.exec_()
        if res:
            _obj.state = DbObject.States.state_pending
            self.objects_pending.append(_obj)
        return res

    def delete(self, _obj):
        assert issubclass(_obj.__class__, DbObject)
        query = self.engine.delete(_obj)
        res = self.sql.exec_(query)
        if res:
            _obj.state = DbObject.States.state_deleted
            self.objects_deleted.append(_obj)
        return res

    def __load_result_to_obj(self,_obj):

        for col in range(0, _obj.get_column_count()):
            f = self.sql.record().field(col).name()
            data = self.sql.value(col)
            _obj.set_data(field=f, data=data)
            _obj.state = DbObject.States.state_persistent

    def __bind_vals(self,_obj):
        for col in range (0, _obj.get_column_count()):
            data = _obj.data(index=col)
            if data is None:
                data = QVariant()
            self.sql.bindValue(":"+_obj.get_field_name(col),data)

    def commit(self):
        res = self.db.commit()
        if res:
            self.db.transaction()
            while self.objects_pending:
                _obj = self.objects_pending.pop(0)
                _obj.state = DbObject.States.state_persistent

            while self.objects_deleted:
                _obj = self.objects_deleted.pop(0)
                _obj.state = DbObject.States.state_detached
                _obj.set_data(field="id",data=QVariant())

            while self.objects_new:
                _obj = self.objects_new.pop(0)
                _obj.state = DbObject.States.state_persistent

        return res

    def rollback(self):
        res = self.db.rollback()
        if res:
            self.db.transaction()

            while self.objects_pending:
                _obj = self.objects_pending.pop(0)
                ok = self.filter("id="+_obj.data(field="id").toString()).one(_obj)
                if ok:
                    _obj.state = DbObject.States.state_persistent
                else:
                    _obj.state = DbObject.States.state_detached
                    _obj.set_data(field="id", data=QVariant())

            while self.objects_deleted:
                _obj = self.objects_deleted.pop(0)
                if not self.objects_new.__contains__(_obj):
                    ok = self.filter("id=" + _obj.data(field="id").toString()).one(_obj)
                    if ok:
                        _obj.state = DbObject.States.state_persistent
                    else:
                        _obj.state = DbObject.States.state_detached
                        _obj.set_data(field="id", data=QVariant())
                else:
                    _obj.state = DbObject.States.state_detached
                    _obj.set_data(field="id", data=QVariant())

            while self.objects_new:
                _obj = self.objects_new.pop(0)
                _obj.state = DbObject.States.state_detached
                _obj.set_data(field="id", data=QVariant())
        return res
