#!/usr/bin/env python
# coding=utf-8
from geyser.item import Item
from geyser.resources_go.types import go_types


class GoItem( Item ):
    def __init__( self, name, parent=None ):
        super( GoItem, self ).__init__( name, parent )

    def Build( self ):
        pass

    def getGoFile( self ):
        pass

    def getGoPackage( self ):
        pass


class GoVar( GoItem ):
    def __init__( self, name, parent, value, const ):
        super( GoVar, self ).__init__( name, parent )
        self.value = value
        self.const = const

    def addType( self, type ):
        self.type = type

    def Build( self ):
        return '\n{defn} {name} {data}'.format( defn = "const" if self.const else "var",
                                                name = self.Name( ),
                                                data = "= {}".format( self.value ) if self.value else self.type
                                                )


class GoVarList( GoItem ):
    def __init__( self, parent ):
        super( GoVarList, self ).__init__( '', parent )

    def addGoVar( self, var ):
        self.addItem( var )

    def Build( self ):
        ls = [ ]
        for var in self.getList( ):
            ls.append( var.Build( ) )
        return ls


class GoType( GoItem ):
    body = '''
type {name} {core} <@
{fields}
@>'''

    def __init__( self, name, parent, core ):
        super( GoType, self ).__init__( name, parent )
        self.fields = [ ]
        self.core = core

    def addField( self, field, is_pointer=False ):
        tf = "{name} {pointer}{type}".format(name = field.Name( ).capitalize( ),
                                             type = field.field.getFullType() if field.isData() else go_types.go_converter(field.getType()),
                                             pointer = "*" if is_pointer else "")
        self.fields.append( tf )

    def addVar( self, name, type, is_pointer=False ):
        tf = "{name} {pointer}{type}".format(name = name,
                                             type = go_types.go_converter(type),
                                             pointer = "*" if is_pointer else "")
        self.fields.append( tf )

    def addMethod( self, name ):
        gm = GoMethodSimple( name, self )
        self.addItem( gm )
        return gm

    def Build( self ):
        src = GoType.body.format( name = self.Name( ),
                                  fields = '\n'.join( "    " + fl for fl in self.fields ),
                                  core = self.core )
        res = src.splitlines( )
        for method in self.getList( ):
            res += method.Build( )
        return res


class GoMethodSimple( GoItem ):
    def __init__( self, name, gotype=None ):
        super( GoMethodSimple, self ).__init__( name, gotype )
        self.args = ""
        self.results = ""
        self.body = ""

    def addBody( self, body ):
        self.body = body

    def getGoType( self ):
        return self.parent

    def addArgs( self, args ):
        self.args = args

    def addResults( self, res ):
        self.results = res

    def Build( self ):
        src = '''\nfunc (self *{type}) {name}({args}) ({results}) <@
{body}
@>
'''.format( name = self.Name( ),
            type = self.parent.Name( ),
            body = self.body,
            args = self.args,
            results = self.results
            )
        return src.splitlines( )


class GoFunctionSimple( GoItem ):
    def __init__( self, name, gofile=None ):
        super( GoFunctionSimple, self ).__init__( name, gofile )
        self.args = ""
        self.results = ""
        self.body = []
        self.comment = ""

    def addBody( self, body ):
        self.body.append(body)

    def addArgs( self, args ):
        self.args = args

    def addResults( self, res ):
        self.results = res

    def addComment(self, comment):
        self.comment = comment

    def Build( self ):
        src = '''{comment}\nfunc {name}({args}){results} <@
{body}
@>
'''.format( name = self.Name( ),
            body = "\n".join(self.body),
            args = self.args,
            results = " ({})".format( self.results ) if self.results else "",
            comment = "\n" + self.comment if self.comment else ""
            )
        return src.splitlines( )


class GoImport( GoItem ):
    def __init__( self, parent ):
        super( GoImport, self ).__init__( None, parent )

    def addImport( self, imp ):
        if self.Find( imp ) is None:
            self.addItem( imp )

    def Build( self ):
        if self.getList( ):
            bimp = "\n".join( '    "{}"'.format( imp ) for imp in self.getList( ) )
            src = '''import (
{}
)'''.format( bimp )
            return src.splitlines( )
        return [ ]
