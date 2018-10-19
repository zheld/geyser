#!/usr/bin/env python
# coding=utf-8
from generator.FSItem.fs_item import FSItem
import os


class Symlink( FSItem ):
    def __init__( self, source, name, parent=None ):
        super( Symlink, self ).__init__( name, parent )
        self.source = source

    def Build( self ):
        try:
            os.symlink( self.source.getPath( ), self.Name() )
        except OSError:
            pass
        except Exception as e:
            print('symlink "{}" create is fail: {}'.format( self.Name(), e ))
