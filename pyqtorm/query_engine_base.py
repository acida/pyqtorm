# -*-  coding: Utf-8 -*-t
from PyQt4.QtSql import QSqlDatabase
from db_object import DbObject
from field import Field


class QueryEngineBase(object):

    st_select = "SELECT {fields} FROM {table} {where} {orderby} {limit} {offset}"
    st_insert = "INSERT INTO {table} ({fields}) VALUES ({values})"
    st_update = "UPDATE {table} SET {values} WHERE id={id}"
    st_delete = "DELETE FROM {table} WHERE id={id}"
    m_db = QSqlDatabase()

    def insert(self, _obj):
        assert issubclass(_obj.__class__,DbObject)
        fields = self.__get_fields(_obj)
        values = [":"+field for field in fields]
        query = self.st_insert.format(table=_obj.table, fields=",".join(fields), values=",".join(values))
        return query

    def update(self, _obj):
        assert issubclass(_obj.__class__, DbObject)
        fields = self.__get_fields(_obj)
        values = [field+"=:" + field for field in fields]
        query = self.st_update.format(table=_obj.table,values=",".join(values), id=_obj.data(field="id").toString())
        return query

    def select(self, _cls, _where=None, _orderby=None, _order=None, _limit=None, _offset=None):

        fields = self.__get_fields(_cls())
        where = ""
        if _where is not None:
            where = "WHERE {where}".format(where=_where)

        orderby = ""
        if _orderby is not None:
            orderby = "ORDER BY {orderby} {order}".format(orderby=_orderby, order=_order)

        limit = ""
        if _limit is not None:
            limit = "LIMIT {cnt}".format(cnt=unicode(_limit))

        offset = ""
        if _offset is not None:
            offset = "OFFSET {cnt}".format(cnt=unicode(_offset))

        query = self.st_select.format(fields=",".join(fields), table=_cls.table, where=where, orderby=orderby, limit=limit, offset=offset)
        return query

    def delete(self, _obj):
        query = self.st_delete.format(table=_obj.table, id=_obj.data(field="id").toString())
        return query

    def db(self):
        return self.m_db

    def open(self):
        return self.m_db.open()

    @staticmethod
    def __get_fields(_obj):
        fields = []
        code = 0x41
        for key in _obj.__dict__:
            member = _obj.__dict__[key]
            if issubclass(member.__class__, Field):
                fields.append(member.field)
                code += 1
        return fields
