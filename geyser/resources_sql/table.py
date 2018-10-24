#!/usr/bin/env python
# coding=utf-8
from geyser.resources_sql.index import *


class Table(Item):
    # Table prototype class
    # Basic class of creating data access modules that provides initial
    # functionality for accessing the table.
    # Warning: the primary key should always be added first!

    def __init__(self, parent):
        super(Table, self).__init__(parent.Name(), parent)
        self.items = parent.items
        self.indexes = []

    def CheckExistsRemoteForeign(self):
        # Checks for the presence of other services in the foreign key table
        for field in self.getFields():
            if field.isForeign() and field.isForeignRemote() is not None:
                return True
        return False

    def addIndex(self, *fields):
        # add index to table
        index = Index(self, *fields)
        self.indexes.append(index)

    def addUniqueIndex(self, *fields):
        # add unique index to table
        index = UniqueIndex(self, *fields)
        self.indexes.append(index)

    def getService(self):
        return self.parent

    def getList(self):
        return self.parent.getList()

    def getFields(self):
        # Get a list of table field objects
        return self.getList()

    def getFieldsName(self):
        # Get a list of table field names
        return [fl.Name() for fl in self.getFields()]

    def getIndexes(self):
        # Get a list of table index objects
        return self.indexes

    def getLen(self):
        # Get the number of fields in the table
        return len(self.getFields())

    def getFieldNumberByName(self, name):
        # Get the ordinal number of a field in the table by name
        for num, fl in enumerate(self.getFields()):
            if name == fl.Name():
                return num
        return None

    def getFieldNumberByField(self, field):
        # Get the ordinal number of the field in the table by field
        for num, fl in enumerate(self.getFields()):
            if field.Name() == fl.Name():
                return num
        return None

    def getIndexByName(self, name):
        # Get a table index by name
        for index in self.indexes:
            if name == index.Name():
                return index
        return None

    def getIdentifier(self):
        for field in self.getList():
            if field.isIdentifier():
                return field
        return None

    def Serialize(self):
        # Get json view of new structure
        result = {}

        field_list = []
        for field in self.getFields():
            field_list.append(field.Serialize())
        result['fields'] = field_list

        index_list = []
        for index in self.getIndexes():
            index_list.append(index.Serialize())
        result['indexes'] = index_list

        # procedure_list = [ ]
        # for method in self.getMethods( ):
        #     procedure_list.append( method( self ).Serialize( ) )
        # result[ 'procedures' ] = procedure_list

        return result
