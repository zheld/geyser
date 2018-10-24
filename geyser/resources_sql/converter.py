#!/usr/bin/env python
# coding=utf-8
import json

from geyser.resources_sql.index import *

FIELDS = 'fields'
NAME = 'name'
INDEXES = 'indexes'
TABLES = 'resources_sql'


class DataBaseConverter:
    # Converts the database of the service according to the architecture, if the service is new - just rolls the base
    # if the base already exists - compares the current structure and a new one, based on the comparison is created
    # script that rolls onto base
    # deleted tables and their infrastructure are not deleted - so far they have just decided to rename them

    def __init__(self, service, struct_file, conf):
        self.service = service
        self.struct_file = struct_file
        self.conf = conf
        self.conn = self._get_connect()
        self.cur = self.conn.cursor()

    def _get_connect(self):
        import psycopg2
        conn = psycopg2.connect(host = self.conf.db_host,
                                port = self.conf.db_port,
                                dbname = self.conf.db_name,
                                user = self.conf.db_user,
                                password = self.conf.db_pswd,
                                )
        return conn

    def _convert(self, sql):
        print("convert db: " + self.conf.db_name + " ...")
        # print(sql)
        self.cur.execute(sql)
        self.conn.commit()
        print("   DONE.")

    def Execute(self):
        # Get the code for creating or updating the table, gets the current structure, runs through the current tables
        # service, and gives the old table (if any) and a new comparison
        body = []
        current_struct = self.GetCurrentStructure()
        new_structure = {}

        new_tables = self.service.getTables()
        old_tables = current_struct[TABLES] if current_struct else {}

        tables = {}
        for new_table in new_tables:
            old_table = old_tables.get(new_table.Name(), None)
            table_converter = TableConverter(old_table, new_table)
            # body += '\n'
            body += table_converter.GetCode()

            tables[new_table.Name()] = new_table.Serialize()

        new_structure[TABLES] = tables
        struct_str = self.getCurrentStructure(new_structure)

        # delete cut tables
        # tables are not deleted, but renamed, then you can delete the type
        for name in old_tables:
            exists = False
            for table in new_tables:
                if table.Name() == name:
                    exists = True
                    break
            if not exists:
                body += TableConverter.GetTableDrop(name)

        # record conversion history
        body += [self.getHistoryConvertCode(struct_str)]

        sql = "\n".join(body)
        self._convert(sql)
        self.cur.close()
        self.conn.close()

        return body

    def getCurrentStructure(self, structure):
        # Write to the file a new structure in json format
        try:
            struct = json.dumps(structure)
            self.struct_file.Write(struct)
            return struct
        except:
            return ""

    def GetCurrentStructure(self):
        # Get the current structure of the service database
        try:
            sql = '''
            SELECT structure
            FROM history_conversions
            WHERE date = ( SELECT max(date) FROM history_conversions )'''

            self.cur.execute(sql)
            try:
                from_db = self.cur.fetchone()[0]
            except Exception as e:
                print("error on query db: " + str(e))
                return ""

            struct_data = from_db

            print("previous struct db: " + struct_data)
            jobject = json.loads(struct_data)
            return jobject
        except Exception as e:
            self.conn.rollback()
            # print("database converter error: " + str(e))
            return ""

    def getHistoryConvertCode(self, struct):
        sql = '''
INSERT INTO history_conversions(structure) VALUES ('{structure}');
        '''.format(structure = struct)
        return sql


class TableConverter:
    def __init__(self, old_table, new_table):
        self.old_table_structure = old_table
        self.table = new_table
        self.rows = []

    def GetCode(self):
        # Get the code for the entire table, with indexes, etc.

        body = []
        if not self.old_table_structure:
            return self.GetAllCreate()
        else:
            body += self.GetDropedIndex()
            body += self.GetDropedFields()

            body += self.GetCreatedFields()
            body += self.GetCreatedIndex()

        return body

    def GetDropedIndex(self):
        # Checks if there are any missing indexes in the new table, is it finds, then returns
        # code to remove them from the current structure

        body = []
        for index in self.old_table_structure[INDEXES]:
            old_index = index[NAME]
            idx = self.table.getIndexByName(old_index)
            if idx is None:
                body += self.GetIndexDrop(old_index)
        return body

    def GetCreatedIndex(self):
        # Checks if there are new indexes in the current structure, if not, then returns
        # code to add them

        body = []
        for index in self.table.getIndexes():
            exists = False
            for old_index in self.old_table_structure[INDEXES]:
                old_index_name = old_index[NAME]
                if index.Name() == old_index_name:
                    exists = True
                    break
            if not exists:
                body += '\n'
                body += self.GetIndexCreate(index)
        return body

    def GetDropedFields(self):
        body = []
        for field in self.old_table_structure[FIELDS]:
            old_field = field[NAME]
            idx = self.table.getFieldNumberByName(old_field)
            if idx is None:
                body += self.GetFieldRemoverd(old_field)
        return body

    def GetCreatedFields(self):
        body = []
        for field in self.table.getFields():
            exists = False
            for old_field in self.old_table_structure[FIELDS]:
                old_field_name = old_field[NAME]
                if field.Name() == old_field_name:
                    exists = True
                    break
            if not exists:
                body += '\n'
                body += self.GetFieldAdded(field)
        return body

    def GetSequenceName(self, field):
        return '{table}_{field}_seq'.format(table = self.table.Name(),
                                            field = field.Name())

    # create objects
    def GetFieldCreate(self, field):
        if field.isIdentifier() and field.isAuto():
            default = " DEFAULT nextval('{name}'::regclass)".format(name = self.GetSequenceName(field))
        else:
            default = ' DEFAULT ' + field.getDefault() if field.getDefault() else ''

        body = '    {name} {type}{default}'.format(name = field.Name(),
                                                   type = field.getType(),
                                                   default = default)

        return body

    def GetFieldAdded(self, field):
        return ['''ALTER TABLE {table} ADD COLUMN {create_field};'''.format(table = self.table.Name(),
                                                                            create_field = self.GetFieldCreate(field))]

    def GetAllCreate(self):
        body = []

        try:
            pkey = self.table.getIdentifier()
            if pkey.isAuto():
                body += self.GetSequenceCreate(pkey)
        except:
            pass

        # table body
        body += self.GetTableCreate()

        # indexes
        for index in self.table.getIndexes():
            body += self.GetIndexCreate(index)

        return body

    def GetTableCreate(self):
        rows = [self.GetFieldCreate(fl) for fl in self.table.getFields()]
        try:
            pkey = self.table.getIdentifier()
            rows += ['    CONSTRAINT {table}_{pkey}_pk PRIMARY KEY ({pkey})'.format(table = self.table.Name(),
                                                                                    pkey = pkey.Name())]
        except:
            pass

        fields = ',\n'.join(rows)

        body = '''
CREATE TABLE {table}
(
{fields}
);'''.format(table = self.table.Name(), fields = fields)
        return body.splitlines()

    def GetIndexCreate(self, index):
        unique = 'UNIQUE' if isinstance(index, UniqueIndex) else ''
        fields = ', '.join(fl.Name() for fl in index.getFields())
        body = '''
CREATE {unique} INDEX {name}
ON {table}
USING btree
({fields});'''.format(name = index.Name(),
                      table = self.table.Name(),
                      fields = fields,
                      unique = unique)
        return body.splitlines()

    def GetSequenceCreate(self, field):
        body = '''
CREATE SEQUENCE {name}
INCREMENT 1
MINVALUE 1
MAXVALUE 9223372036854775807
START 1
CACHE 1;
    '''.format(name = self.GetSequenceName(field))
        return body.splitlines()

    # drop objects
    def GetFieldRemoverd(self, name):
        # Получить код удаления столбца таблицы
        return ['''ALTER TABLE {table} DROP COLUMN {field};'''.format(table = self.table.Name(),
                                                                      field = name)]

    @classmethod
    def GetTableDrop(cls, name):
        return ['''ALTER TABLE {table} RENAME TO {table}_deleted;'''.format(table = name)]

    def GetIndexDrop(self, name):
        return ['''DROP INDEX {index};'''.format(index = name)]

    def GetSequenceDrop(self, field):
        return ['''DROP SEQUENCE "{table}_{field}_seq";'''.format(table = self.table,
                                                                  field = field.Name())]
