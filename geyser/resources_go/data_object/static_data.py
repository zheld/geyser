#!/usr/bin/env python
# coding=utf-8
from geyser.resources_go.data_object.data import GoDataObject


class GoStaticData( GoDataObject ):
    def __init__( self, name, parent=None, public=True ):
        super( GoStaticData, self ).__init__( name, parent )
        self.functions = [
        ]

    def createGoType(self):
        pass

    def BuildCustom( self ):
        for field in self.getFields():
            self.gofile.addVar(field.Name(), None, field.getType())

    def addData( self, name, data ):
        return self.addField( name, data.typeName( ), None )

    def addArrayData( self, name, data ):
        return self.addArray( name, "" )

