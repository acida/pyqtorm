# -*-  coding: Utf-8 -*-t
from os import path
from PyQt4.QtSql import QSqlDatabase
from query_engine_base import QueryEngineBase


class QueryEngineLite(QueryEngineBase):

    path = ""

    def __init__(self, _path):
        assert path.exists(_path)
        self.path = _path
        self.m_db = QSqlDatabase.addDatabase("QSQLITE")
        self.m_db.setHostName("localHost")
        self.m_db.setDatabaseName(self.path)

    def get_path(self):
        return path
