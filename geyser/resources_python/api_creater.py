#!/usr/bin/env python
# coding=utf-8


class APICreater:
    def __init__( self, api_file, start_file ):
        self.api_file = api_file
        self.start_file = start_file
        header_rows = '''
if __name__ == "__main__":
    api = {
        '''
        self.start_file.addRowsBlock( header_rows )
        self.calling_rows = self.start_file.addRowsBlock( '' )
        footer_rows = '''    }
    app_start( api )
        '''
        self.start_file.addRowsBlock( footer_rows )

    def addAPIMethod( self, classname, methodname, args_exists, parent ):
        # file start
        if parent:
            imp = 'from src.{filename} import {classname}'.format( filename = parent,
                                                                   classname = classname )
            self.api_file.addImport( imp )

        procedure = '{}_{}'.format( classname.lower( ), methodname.lower( ) )
        foreign_method = "        '{procedure}': {procedure},".format( procedure = procedure )
        self.calling_rows.addRows( foreign_method )

        # file api
        body = '''try:
    res = yield {classname}.{method}({args})
    response.write(to_pack(res))
except Exception as err:
    msg = "Unable to {classname}.{method} from {parent}: " + str(err)
    publish_error(msg)
    response.error(ITEM_IS_ABSENT, msg)
finally:
    response.close()
        '''.format( classname = classname,
                    method = methodname,
                    args = '*args' if args_exists else '',
                    parent = parent or classname )

        foo = self.api_file.addFunction( procedure, [ 'args', 'response' ], [ '@unpacker', '@asynchronous' ] )
        foo.addBody( body )
