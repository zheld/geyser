import os
from generator.FSItem.fs_item import FSItem
from generator.FSItem.file import File
from generator.FSItem.symlink import Symlink
from generator.FSItem.dir_copy import CopyDirectory


class Directory(FSItem):
    def __init__(self, name, parent=None):
        super(Directory, self).__init__(name, parent)

    def Build(self):
        print("directory: ", self.Name())
        # create a directory if there is none
        if self.Name():
            try:
                os.mkdir(self.getPath())
                print('Directory created [{}]'.format(self.Name()))
            except Exception as e:
                pass

            self.ComeIn()

        for item in self.getList():
            item.Build()

        self.GoOut()

    def ComeIn(self):
        # enter directory
        os.chdir(self.getPath())

    def GoOut(self):
        # exit directory
        if self.parent:
            os.chdir(self.parent.getPath())
        else:
            os.chdir('..')
        return self.parent

    def addDirectory(self, name):
        # add nested directory
        dir = Directory(name, self)
        self.addItem(dir)
        return dir

    # Go
    def addGoPackage(self, name):
        # add python nested package
        from generator.Go.gopackage import GoPackage
        pkg = GoPackage(name, self)
        self.addItem(pkg)
        return pkg

    def addGoFile(self, name, package_name=None, only_create=False):
        # attach python file
        from generator.Go.gofile import GoFile
        gf = GoFile(name, self, package_name, only_create)
        self.addItem(gf)
        return gf

    # Python
    def addPackage(self, name):
        # add python nested package
        from generator.Python.package import Package
        pkg = Package(name, self)
        self.addItem(pkg)
        return pkg

    def addPyFile(self, name, only_create=False):
        # attach python file
        from generator.Python.pyfile import PyFile
        pf = PyFile(name, self, only_create = only_create)
        self.addItem(pf)
        return pf

    # Json
    def addJsonFile(self, name, only_create=False):
        # attach json file
        from generator.Json.jsonfile import JsonFile
        f = JsonFile(name, self, only_create = only_create)
        self.addItem(f)
        return f

    def addSQLFile(self, name, only_create=False):
        # attach sql file
        from generator.SQL.sql_file import SQLFile
        sql = SQLFile(name, self, only_create = only_create)
        self.addItem(sql)
        return sql

    def addSymLink(self, fsitem, name):
        # add file system object reference
        sl = Symlink(fsitem, name, self)
        self.addItem(sl)
        return sl

    def addCopyDirectory(self, fsitem, name):
        # add file system object reference
        dc = CopyDirectory(fsitem, name, self)
        self.addItem(dc)
        return dc

    def addCopyFile(self, fsitem, name, only_create=True):
        # create a copy of the file in the directory if you need to overwrite the file
        # then you need to pass the parameter only_create = False
        fl = File(name, self, only_create = only_create)
        text = fsitem.Read()
        fl.body.append(text)
        self.addItem(fl)
        return fl
