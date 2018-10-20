import subprocess

from generator.FSItem.fs_item import FSItem

head = '''
{comm}
{comm} Document generated automatically by GEYSER v0.01
{comm}
{comm} Warning: any edits to this file will be lost
{comm}
'''

lng_comm = {"golang": "//", "python": "#", "sql": "--", "c++": "//"}


class File(FSItem):
    def __init__(self, name, lang, parent=None, only_create=False):
        super(File, self).__init__(name, parent)
        self.lang = lang
        self.only_create = only_create
        self.body = []
        self.execute = False

    def _createHeaderFile(self):
        if self.lang == "":
            return ""
        comm = lng_comm[self.lang]
        return head.format(comm = comm)

    def Build(self):
        for item in self.getList():
            build = item.Build()
            if isinstance(build, list):
                build = '\n'.join(build)
            self.body.append(build)
        fl = '\n'.join(self.body)
        self.Save(self._createHeaderFile() + fl)

    def Save(self, fl_str):
        if self.only_create:
            try:
                fl = open(self.getPath())
                fl.close()
                return
            except:
                pass

        fl_str = fl_str.replace("@>", "}")
        fl_str = fl_str.replace("<@", "{")
        # Create or overwrite file in current directory
        fl = open(self.Name(), 'w')
        fl.write(fl_str)

        # if required, makes it executable
        if self.execute:
            subprocess.call('chmod u+x {filename}'.format(filename = self.Name()), shell = True)

        fl.close()

    def Read(self):
        try:
            fl = open(self.getPath())
            text = fl.read()
            fl.close()
            return text
        except IOError:
            return ''

    def Write(self, body):
        if isinstance(body, str):
            body = [body]
        self.body += body

    def addExecMode(self):
        self.execute = True
