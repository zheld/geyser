import subprocess
from generator.FSItem.fs_item import FSItem


class File( FSItem ):
    def __init__( self, name, parent=None, only_create=False ):
        super( File, self ).__init__( name, parent )
        self.only_create = only_create
        self.body = [ ]
        self.execute = False

    def Build( self ):
        for item in self.getList( ):
            build = item.Build( )
            if isinstance( build, list ):
                build = '\n'.join( build )
            self.body.append( build )
        fl = '\n'.join( self.body )
        self.Save( fl )

    def Save( self, fl_str ):
        if self.only_create:
            try:
                fl = open( self.getPath( ) )
                fl.close( )
                return
            except:
                pass

        fl_str = fl_str.replace( "@>", "}" )
        fl_str = fl_str.replace( "<@", "{" )
        # Создать или перезаписать файл в текущей директории
        fl = open( self.Name( ), 'w' )
        fl.write( fl_str )

        # если требуется - делает запускаемым
        if self.execute:
            subprocess.call( 'chmod u+x {filename}'.format( filename = self.Name( ) ), shell = True )

        fl.close( )

    def Read( self ):
        try:
            fl = open( self.getPath( ) )
            text = fl.read( )
            fl.close( )
            return text
        except IOError:
            return ''

    def Write( self, body ):
        if isinstance( body, str ):
            body = [ body ]
        self.body += body

    def addExecMode( self ):
        self.execute = True
