#!/usr/bin/env python
# coding=utf-8
from resources_go.data_object.go_methods.insert import InsertGoMethod
from resources_go.data_object.go_methods.insert_read import InsertReadGoMethod
from resources_go.data_object.go_methods.delete import Delete
from resources_go.data_object.go_methods.list import List
from resources_go.data_object.go_methods.list_filter import ListFilter
from resources_go.data_object.go_methods.read import ReadGoMethod
from resources_go.data_object.go_methods.string import StringGoMethod
from resources_go.data_object.go_methods.update import UpdateGoMethod
from resources_go.data_object.go_methods.set import UpdateByGoMethod
from resources_go.data_object.go_methods.get_id import GetId
from resources_go.data_object.go_methods.upsert import UpsertGoMethod
from resources_go.data_object.go_methods.read_by_unique import ReadByUnique
from resources_go.data_object.go_methods.insert_read_light import InsertReadGoLight

from resources_go.data_object.go_methods.new import NewGoMethod
from resources_sql.table import *
from resources_sql.table_dictionary import *
from resources_go.data_object.go_methods.fields import Fields
from resources_go.data_object.extensions.static_dict import StaticDict
from resources_go.data_object.extensions.cache_id import CacheID
from resources_sql.field import *

class GoDataObject( Item ):
    def __init__( self, name, parent=None, public=True ):
        super( GoDataObject, self ).__init__( name, parent )
        self.table = None
        # self.outside_tables = [ ]
        self.static_var = [ ]
        self.inside_data_list = [ ]

        # extensions
        self.extensions = []
        self.extensions_file = None

        # sql file for db procedure
        self.sql_file = None

        # unique set fields
        self.unique_field_set = [ ]

        # add into client
        self.in_client = False

        # type name
        split_name = name.split( "_" )
        sname = "".join(n.capitalize() for n in split_name)
        self.typeName = "DBI_" + sname

        # get id
        self.has_get_id = False

        self.gopackage = None
        self.gofile = None
        self.gotype = None
        self.functions = [ StringGoMethod,
                           GetId,
                           ReadByUnique,
                           NewGoMethod,
                           ReadGoMethod,
                           InsertReadGoMethod,
                           InsertReadGoLight,
                           InsertGoMethod,
                           UpdateGoMethod,
                           UpdateByGoMethod,
                           Fields,
                           # ReadAll,
                           List,
                           ListFilter,
                           Delete,
                           UpsertGoMethod,
                           ]
        self.meta_field = [ ]
        self.extend_data_list = [ ]

    def addMetaField( self, name, type, is_pointer=False ):
        self.meta_field.append( [ name, type, is_pointer ] )

    def hasGetId( self ):
        self.has_get_id = True

    def Build( self, src_dir, sql_file, go_compiler ):
        self.sql_file = sql_file
        self.go_compiler = go_compiler
        # Получить код нативного пакета этой таблицы
        self.gopackage = src_dir.addGoPackage( self.Name().lower() )

        # build children data
        for data in self.inside_data_list:
            data.Build( self.gopackage, sql_file, go_compiler )

        # if not self.getFields():
        #     return

        self.gofile = self.gopackage.addGoFile( "{}.data".format( self.Name().lower() ) )
        self.gofile_bl = self.gopackage.addGoFile( "{}.bl".format( self.Name().lower() ), only_create = True )

        # create signature index
        if self.table:
            self.table.addIndex( *self.unique_field_set )

        # custom code
        self.BuildCustom()

        # add imports
        for field in self.getFields():
            t = field.getType()
            if t == go_types.timestamp:
                self.gofile.addImport( "time" )
            # если поле это целый объект:
            if field.isData():
                self.gofile.addImport(field.field.getPackageName())

        # gofile var
        for stvar in self.static_var:
            type = ""
            for type in stvar.getType():
                if not isinstance( type, str ):
                    self.gofile.addImport( type.getImport() )
                    type = type.getFullType()
                else:
                    type = go_types.go_converter(type)
            self.gofile.addVar( stvar.Name(), stvar.default, type, stvar.const )

        # extensions
        for extension in self.extensions:
            if extension:
                extension.getNative(self.go_compiler)

        # methods
        if self.getLen():
            # gotype
            self.createGoType()

            # functions native
            for method_class in self.getMethods():
                meth = method_class( self )
                if meth:
                    meth.getNative()
                    meth.getSqlProcedure()

    def build_outside_fields( self ):
        if len( self.extend_data_list ) != 0:
            exist_list_position = 1
            if not self.getIdentifier():
                exist_list_position = 0
            exist_field = Field( "exist_list", self, go_types.vbit)
            self.items.insert( exist_list_position, exist_field )

            for extdata in self.extend_data_list:
                pass

    def BuildCustom( self ):
        pass

    def addStaticDict(self, name, seq, default=""):
        stdic = StaticDict(self, name, seq, default)
        self.extensions.append(stdic)
        return stdic

    def addCacheId(self):
        ci = CacheID(self)
        self.extensions.append(ci)
        return ci

    def createGoType( self ):
        self.gotype = self.gofile.addType( self.typeName )
        for field in self.getFields():
            self.gotype.addField( field )
        # meta o_sequence
        for field in self.meta_field:
            self.gotype.addVar( *field )

    def createProxyBlock( self, pyfile ):
        # Получить код проксирующих методов статического класса таблицы для папки services_api
        cls = pyfile.addClass( self.Name() )
        for method_class in self.getMethods():
            method_class( self ).getProxy( cls )

    def addVarSimple( self, name, type, value=None, const=False ):
        type = [ type ]
        return self.addStaticField( name, type, value, const )

    def addVarSlice( self, name, type, is_pointer=True ):
        # type = [ type ]
        value = "[]{}{}<@@>".format( "*" if is_pointer else "", go_types.go_converter(go_types.go_converter(type if isinstance(type, str) else
                                                                                                        type.getFullType())))
        return self.addStaticField( name, [ type ], value )

    def addVarMap( self, name, key_type, value_type ):
        type = [ key_type, value_type ]
        value = "make(map[{}]{})".format(go_types.go_converter(key_type),
                                         go_types.go_converter(value_type if isinstance(value_type, str) else
                                                              "{}.{}".format( value_type.Name(), value_type.getType() )))
        return self.addStaticField( name, type, value )

    def addStaticField( self, name, type=None, value=None, const=False ):
        sf = Field( name, self, type, value, False, const )
        self.static_var.append( sf )
        return sf

    def addSignatureRowIndex( self, *fields ):
        '''
        уникальный набор полей, по которому можно идентифицировать объект
        применяется для методов типа Update и Create
        :param fields:
        :return:
        '''
        self.unique_field_set = fields
        self.table.addUniqueIndex( *fields )

    def addInToClient( self ):
        self.in_client = True

    def addData( self, name ):
        data = GoDataObject( name, self )
        self.inside_data_list.append( data )
        return data

    def addDataField( self, name, data_object ):
        idf = data_object.getIdentifier()
        if idf:
            type = idf.getType()
        else:
            raise Exception("объект без первичного ключа")
        return self.addField( name, type, field = data_object )

    def addTable( self ):
        ''' add table with primary key
        :return: table
        '''
        if self.getIdentifier():
            table = TableWithPrimaryKey( self )
        else:
            table = Table( self )
        self.table = table
        return table

    def addOutsideField( self, name, type, history=False, one_to_many=False ):

        data = self.addData( "{}_{}".format( self.Name(), name ) )
        id = data.addIdentifierNoAuto()
        if isinstance( type, Field ):
            if one_to_many:
                value = data.addForeignOneToMany( type, name )
            else:
                value = data.addForeignOneToOne( type, name )
        table = data.addTable()
        table.addIndex( id )
        self.extend_data_list.append( data )

        # if history:
        #     hdata = self.addData( "{}_{}_history".format( self.Name( ), name ) )
        #     hid = hdata.addIdentifierNoAuto( )
        #     hdata.addField( "value", value.getType() )
        #     hdata.addAutoTimeStamp( "change_dt" )
        #     htable = hdata.addTable( )
        #     htable.addIndex( hid )

    def addField( self, name, type, default=None, const=False, primary=False, field=None, auto=None ):
        new_field = Field( name, self, type, default, primary, const, field, auto, False )
        self.addItem( new_field )
        return new_field

    def addConstField( self, name, type, default=None, primary=False, field=None, auto=None ):
        new_field = Field( name, self, type, default, primary, True, field, auto, False )
        self.addItem( new_field )
        return new_field

    def addArray( self, name, type ):
        new_field = Field( name, self, type, None, False, False, None, None, True )
        self.addItem( new_field )
        return new_field

    def addAutoTimeStamp( self, name ):
        # добавление автоматически генерируемого поля типа timestamp
        return self.addField(name, go_types.timestamp, default = 'now()', auto = True, const = True)

    def addAutoDate( self, name ):
        # добавление автоматически генерируемого поля типа date
        return self.addField(name, go_types.date, default = 'now()::DATE', auto = True, const = True)

    def addForeignOneToOne( self, field, name=None ):
        # добавление поля типа внешняя ссылка
        if not name:
            foreign_data = field.getDataObject()
            name = "{}{}".format( foreign_data.Name(), field.Name() )
        return self.addField( name, field.getType(), field = field )

    def addForeignOneToMany( self, field, name=None ):
        if not name:
            foreign_data = field.getDataObject()
            name = "{}{}_list".format( foreign_data.Name(), field.Name() )
        return self.addField( name, field.getType() + "[]", field = field )

    def addConstForeign( self, field ):
        # добавление поля типа внешняя ссылка
        return self.addField(field.Name(), go_types.integer, field = field, const = True)

    def addIdentifier(self, type=go_types.integer):
        # добавляет первичный ключ таблицы
        name = 'id'
        new_field = Field( name, self, type, primary = True, auto = True )
        if len( self.items ) != 0:
            raise Exception( 'Первичный ключ должен быть добавлен первым!' )
        self.addItem( new_field )
        return new_field

    def addIdentifierNoAuto(self, type=go_types.integer):
        # добавляет первичный ключ таблицы
        name = "id"
        new_field = Field( name, self, type, primary = True, auto = False )
        if len( self.items ) != 0:
            raise Exception( 'Первичный ключ должен быть добавлен первым!' )
        self.addItem( new_field )
        return new_field

    def CheckExistsRemoteForeign( self ):
        # Проверяет на наличие в таблице внешних ключей других сервисов
        for field in self.getFields():
            if field.isForeign() and field.isForeignRemote() is not None:
                return True
        return False

    def getTables( self ):
        tables = [ ]
        if self.table:
            tables.append( self.table )
        for data in self.inside_data_list:
            tables += data.getTables()

        return tables

    def getImport( self ):
        imp = [ ]
        current = self
        while True:
            if isinstance( current, GoDataObject ):
                imp.append( current.Name() )
                current = current.parent
            else:
                break
        imp.reverse()
        return "/".join( imp )

    def getType( self ):
        return self.typeName

    def getService( self ):
        # Получить объект сервиса таблицы
        current = self
        while True:
            if current.parent:
                current = current.parent
            else:
                return current

    def getFields( self ):
        # Получить список объектов полей таблицы
        return self.getList()

    def getFieldsName( self ):
        # Получить список имен полей таблицы
        return [ fl.Name() for fl in self.getFields() ]

    def getLen( self ):
        # Получить количество полей
        return len( self.getFields() )

    def getFieldNumberByName( self, name ):
        # Получить порядковый номер поля
        for num, fl in enumerate( self.getFields() ):
            if name == fl.Name():
                return num
        return None

    def getFieldNumberByField( self, field ):
        # Получить порядковый номер поля по полю
        for num, fl in enumerate( self.getFields() ):
            if field.Name() == fl.Name():
                return num
        return None

    def getMethods( self ):
        # Получить методы таблицы
        return self.functions

    def getModifiedFields( self ):
        # Получить все поля таблицы, которые можно модифицировать
        return [ fld for fld in self.getFields() if not fld.isConst() ]

    def getIdentifier( self ):
        for field in self.getList():
            if field.isIdentifier():
                return field
        return None

    def GetFieldsWithoutIdentifier( self ):
        # Получить список объектов полей без первичного ключа
        res = [ ]
        for field in self.getFields():
            if not field.isIdentifier():
                res.append( field )
        return res

    def getFullType( self ):
        return "{}.{}".format( self.Name(), self.getType() )

    def getPackageName( self ):
        return self.Name()

    def getDataObject(self):
        return self
