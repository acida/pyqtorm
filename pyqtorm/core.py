# -*-  coding: Utf-8 -*-t
from PyQt4.QtGui import QMessageBox
from PyQt4.QtCore import QString
from PyQt4.QtSql import QSqlDatabase
from transaction import Transaction


class Core(object):

    engine = None
    model_classes = []
    cnt = 0

    def start(self, _engine):
        self.engine = _engine
        if not self.engine.open():
            message = QMessageBox()
            message.setWindowTitle(u'Предупреждение')
            message.setText(QString(u'Не удалось открыть базу данных'))
        else:
            print "database opened"

    def register_model_class(self, _cls):
        self.model_classes.append(_cls)

    def get_engine(self):
        return self.engine

    def new_transaction(self):
        self.cnt += 1
        s = Transaction(QSqlDatabase.cloneDatabase(self.engine.db(),QString.number(self.cnt)),self)
        return s

