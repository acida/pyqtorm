# -*-  coding: Utf-8 -*-t

from PyQt4.QtCore import QVariant, QAbstractTableModel, Qt, QModelIndex


class EditStrategy(object):
    OnFieldChange = 0
    OnRowChange = 1
    OnManualSubmit = 2


class TableModel(QAbstractTableModel):

    def __init__(self, _transaction, _cls, parent=None):
        QAbstractTableModel.__init__(self,parent)
        self.transaction = _transaction
        self.cls = _cls
        self.filter = None
        self.rows = []
        self.headers = {Qt.Horizontal: {Qt.DisplayRole: []}}
        _obj = self.cls()
        self.column_cnt = _obj.get_column_count()-1
        self.row_cnt = 0
        self.dflags = {}
        self.edit_strategy = EditStrategy.OnManualSubmit
        self.rows_deleted_numbers = []
        for col in range(0, self.column_cnt):
            self.headers[Qt.Horizontal][Qt.DisplayRole].append(_obj.get_field_headers(col+1))

    def setFilter(self, _filter):
        self.filter = _filter

    def submit(self):
        return True

    def submitAll(self):
        obj_deleted = list(self.transaction.get_objects_deleted())
        res = self.transaction.commit()
        if res:
            while obj_deleted:
                _obj = obj_deleted.pop(0)
                _obj.disconnect(_obj, _obj.signal_data_changed, self.on_db_object_data_changed)

        return res

    def revert(self):
        return True

    def revertAll(self):

        objects_to_remove = list(self.transaction.get_objects_new())
        objects_to_add = list(reversed(self.transaction.get_objects_deleted()))
        indexes_to_add = self.rows_deleted_numbers
        res = self.transaction.rollback()
        if res:
            while objects_to_remove:
                _obj = objects_to_remove.pop(0)
                _row = self.rows.index(_obj)
                self.beginRemoveRows(QModelIndex(), _row, _row)
                self.rows.pop(_row)
                self.row_cnt -= 1
                self.endRemoveRows()

            while objects_to_add:
                _obj = objects_to_add.pop(0)
                _row = indexes_to_add.pop(0)
                self.beginInsertRows(QModelIndex(), _row, _row)
                self.row_cnt += 1
                self.rows.insert(_row, _obj)
                self.endInsertRows()

        return res

    def revertRow(self, row):
        pass

    def on_db_object_data_changed(self, column):
        if (self.rows.__contains__(self.sender())):
            index = self.index(self.rows.index(self.sender()),column)
            self.dataChanged.emit(index, index)

    def select(self):
        res = False
        while self.row_cnt > 0:
            self.removeRow(0)
        self.rows = self.transaction.filter(self.filter).all(self.cls, self, self.on_db_object_data_changed)
        self.beginInsertRows(QModelIndex(), 0, len(self.rows)-1)

        self.endInsertRows()
        self.row_cnt = len(self.rows)
        if self.row_cnt > 0:
            res = True
        return res


    def setEditStrategy(self, _strategy):
        assert isinstance(_strategy, EditStrategy)

    def setFlag(self, index, flag):
        self.dflags[index] = flag

    def flags(self, index):
        res = Qt.ItemIsEnabled
        if index.isValid():
            res = Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable
            if self.dflags.__contains__(index):
                res = self.dflags[index]
        return res

    def headerData(self, _section, _orientation=Qt.Horizontal, _role=Qt.DisplayRole):
        res = QVariant()
        if self.headers.__contains__(_orientation):
            if self.headers[_orientation].__contains__(_role):
                if len(self.headers[_orientation][_role])>_section:
                    res = self.headers[_orientation][_role][_section]
        return res

    def setHeaderData(self, _section, _orientation=Qt.Horizontal, data=QVariant(), _role=Qt.DisplayRole):
        if self.column_cnt <= _section or data.isNull():
            res = False
        else:
            if not self.headers.__contains__(_orientation):
                self.headers[_orientation] = {}
            if not self.headers[_orientation].__contains__(_role):
                self.headers[_orientation][_role] = []
                for col in range(0,self.column_cnt):
                    self.headers[_orientation][_role].append(QVariant())
            self.headers[_orientation][_role][_section] = data
            res = True
        return res

    def removeRows(self, row, count, parent=None, *args, **kwargs):
        res = False
        if count < 1 or (row + count - 1) >= self.rowCount() or row < 0:
            res = False
        else:
            res = True
            self.beginRemoveRows(parent, row, (row+count-1))
            for i in range(0,count):
                self.rows_deleted_numbers.insert(0,row)
                _obj = self.rows.pop(row)
                self.transaction.delete(_obj)
                self.row_cnt -= 1
            self.endRemoveRows()
        return res

    def insertRows(self, row, count, parent=None, *args, **kwargs):
        self.beginInsertRows(parent, row, row + count - 1)
        for var in range(row, row + count):
            _obj = self.cls()
            _obj.setParent(self)
            _obj.connect(_obj, _obj.signal_data_changed, self.on_db_object_data_changed)
            self.rows.insert(var, _obj)
            self.transaction.add(_obj)
            self.row_cnt += 1
        self.endInsertRows()
        return True

    def setData(self, index, data, role=Qt.EditRole):
        res = False
        if index.isValid():
            if role == Qt.EditRole:
                _obj = self.rows[index.row()]
                _obj.disconnect(_obj, _obj.signal_data_changed, self.on_db_object_data_changed)
                _obj.set_data(index=index.column()+1, data=data)
                _obj.connect(_obj, _obj.signal_data_changed, self.on_db_object_data_changed)
                res = self.transaction.update(_obj)
                self.dataChanged.emit(index, index)
        return res

    def data(self, index, role=Qt.DisplayRole):
        res = QVariant()
        if index.isValid():
            if role == Qt.EditRole  or  role == Qt.DisplayRole:
                _obj = self.rows[index.row()]
                res = _obj.data(index=index.column()+1)
        return  res

    def columnCount(self, parent=None, *args, **kwargs):
        return self.column_cnt

    def rowCount(self, parent=None, *args, **kwargs):
        return self.row_cnt


