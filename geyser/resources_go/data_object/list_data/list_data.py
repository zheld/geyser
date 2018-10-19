#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.data import GoDataObject
from resources_go.types import go_types
from .add import AddListDataGoMethod
from .get import GetListDataGoMethod
from .len import LenListDataGoMethod


class GoDataList( GoDataObject ):
    def __init__( self, name, type, parent=None, pointer=True, public=True ):
        super( GoDataList, self ).__init__( name, parent )
        self.value_type = type
        self.is_pointer = pointer
        self.functions = [
            AddListDataGoMethod,
            # RemoveListDataGoMethod,
            LenListDataGoMethod,
            GetListDataGoMethod,

        ]

    def createGoType( self ):
        pass

    def BuildCustom( self ):
        self.addVarSlice( "{}_list".format( self.value_type.Name( ) ), self.value_type, self.is_pointer )
        # functions native
        for method_class in self.getMethods( ):
            method_class( self ).getNative( )

    def getValueType( self ):
        return "{}.{}".format( self.value_type.Name( ), self.value_type.getType( ) ) if not isinstance( self.value_type, str ) else go_types.go_converter(self.value_type)
