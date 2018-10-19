#!/usr/bin/env python
# coding=utf-8
from .table_pkey import TableWithPrimaryKey


class TableDictionary( TableWithPrimaryKey ):
    # DataObject extension, providing functionality for accessing table data not only from the database, but also
    # from the RAM cache. Expanded by service methods of providing data for its proxying methods, which
    # unwrap the cache on your side:

    def LoadBase( self, _from, limit ):
        pass
