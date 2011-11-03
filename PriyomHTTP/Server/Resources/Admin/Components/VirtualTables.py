# encoding=utf-8

__all__ = ["VirtualColumn", "StormColumn", "ReferenceColumn", "IDColumn", "ModifiedColumn", "CreatedColumn", "TimestampColumn", "VirtualTable", "ReferencingTable", "Sortable", "Filterable"]

from libPriyom import Formatting
from storm.locals import *
from storm.expr import *
import itertools
from libPriyom import Formatting
from PriyomHTTP.Server.Resources.Admin.Components.Base import ParentComponent

Sortable = 1
Filterable = 2
        
class VirtualColumn(object):
    flags = frozenset()
    
    def __init__(self, title, name=None, formatter=None, width=None, defaultSort=u"ASC", **kwargs):
        super(VirtualColumn, self).__init__(**kwargs)
        self.title = title
        self.name = name or title
        self.formatter = formatter or unicode
        self.width = width
        self.defaultSort = defaultSort
        
    def __contains__(self, flag):
        return flag in self.flags
        
    def _directionToStorm(self, direction):
        return {
            "ASC": Asc,
            "DESC": Desc,
        }[direction]
        
    def getFormattedValue(self, returnedTuple):
        return self.formatter(self.getRawValue(returnedTuple))
    
    def sortResultSet(self, resultSet, direction):
        if not Sortable in self:
            raise TypeError("Cannot sort by {0} column.".format(self.title))
        return resultSet.order_by(*self.stormSort(direction))
        
        
class StormColumn(VirtualColumn):
    def __init__(self, title, stormColumn, **kwargs):
        super(StormColumn, self).__init__(title, **kwargs)
        self.stormColumn = stormColumn
        self.flags = frozenset((Sortable,))
    
    def stormArgs(self):
        return ()
    
    def stormColumns(self):
        return ()
        
    def stormSortArgs(self):
        return ()
        
    def stormSort(self, direction):
        return (self._directionToStorm(direction)(self.stormColumn),)
    
    def getRawValue(self, returnedTuple):
        return getattr(returnedTuple[0], self.stormColumn.name)

class ReferenceColumn(VirtualColumn):
    def __init__(self, title, reference, remoteClass, attributeName, sortingColumns=None, disableFiltering=False, **kwargs):
        if reference._on_remote:
            raise ValueError("References being on the remote are not supported!")
        localClass = reference._cls
        super(ReferenceColumn, self).__init__(title, **kwargs)
        self.localClass = localClass
        self.remoteClass = remoteClass
        self.reference = reference
        self.localKey = reference._local_key
        self.remoteKey = reference._remote_key
        self.attributeName = attributeName
        flags = set()
        if not disableFiltering:
            flags.add(Filterable)
        if sortingColumns is None:
            self.sortingColumns = sortingColumns
        else:
            flags.add(Sortable)
            self.sortingColumns = list(sortingColumns)
        self.flags = frozenset(flags)
    
    def stormArgs(self):
        return ()
    
    def stormColumns(self):
        return ()
        
    def stormSortArgs(self):
        return (self.localKey == self.remoteKey,)
    
    def stormSort(self, direction):
        if self.sortingColumns is None:
            return
        return tuple((self._directionToStorm(direction)(col) for col in self.sortingColumns))
    
    def getFilterIterable(self, store):
        return iter(store.find(self.remoteClass, self.localKey == self.remoteKey).config(distinct=True))
    
    def getRawValue(self, returnedTuple):
        return getattr(returnedTuple[0], self.attributeName)

"""class ReferenceChainColumn(VirtualColumn):
    def __init__(self, title, referenceChain, sortingColumns=None, disableFiltering=False, **kwargs):
        super(ReferenceChainColumn, self).__init__(title, **kwargs)
        self.chain = referenceChain
        flags = set()
        if not disableFiltering:
            flags.add(Filterable)
        if sortingColumns is None:
            self.sortingColumns = sortingColumns
        else:
            flags.add(Sortable)
            self.sortingColumns = list(sortingColumns)
        self.flags = frozenset(flags)
    
    def stormArgs(self):
        return tuple((reference._local_key == reference._remote_key for reference in self.chain[:-1]))
    
    def stormColumns(self):
        """

class IDColumn(StormColumn):
    def __init__(self, stormClass, title=u"ID", name=u"ID", **kwargs):
        super(IDColumn, self).__init__(title, stormClass.ID, name=name, **kwargs)

class TimestampColumn(StormColumn):
    def __init__(self, title, stormColumn, formatter=None, **kwargs):
        super(TimestampColumn, self).__init__(title, stormColumn, formatter=(formatter or Formatting.Formatters.catchNone(Formatting.Formatters.Timestamp())), **kwargs)
        
class CreatedColumn(TimestampColumn):
    def __init__(self, stormClass, title=u"Created", **kwargs):
        super(CreatedColumn, self).__init__(title, stormClass.Created, defaultSort=u"DESC", **kwargs)
        
class ModifiedColumn(TimestampColumn):
    def __init__(self, stormClass, title=u"Modified", **kwargs):
        super(ModifiedColumn, self).__init__(title, stormClass.Modified, defaultSort=u"DESC", **kwargs)

class ReferencingTable(object):
    def __init__(self, name, cls, matchIdTo, displayName = None):
        self.name = name
        self.displayName = displayName or name
        self.cls = cls
        self.matchIdTo = matchIdTo
    
    def select(self, virtualTable, instance, sortColumn=None, sortDirection=u"ASC"):
        return virtualTable.select(sortColumn or virtualTable.columns[0], sortDirection, self.matchIdTo == instance.ID)

class VirtualTable(ParentComponent):
    def __init__(self, name, cls, *args, **kwargs):
        if cls is None:
            raise ValueError(u"VirtualTable must have a class assigned")
        self.description = kwargs.get(u"description", u"")
        if u"where" in kwargs:
            self.where = kwargs[u"where"]
            del kwargs[u"where"]
        else:
            self.where = None
        
        if u"columns" in kwargs:
            self.columns = kwargs[u"columns"]
            del kwargs[u"columns"]
        else:
            self.columns = []
        
        if u"referencingTables" in kwargs:
            self.referencingTables = kwargs[u"referencingTables"]
            del kwargs[u"referencingTables"]
        else:
            self.referencingTables = []
        
        self.name = name
        self.cls = cls
        if len(self.columns) == 0:
            raise ValueError(u"Must have a list of columns")
        
        #self.stormColumns = tuple(column.stormColumn for column in self.columns)
        self.columns = tuple(self.columns)
        self.columnMap = dict(((column.name, column) for column in self.columns))
        self.referencingTableMap = dict(((table.name, table) for table in self.referencingTables))
        super(VirtualTable, self).__init__(None, *args, **kwargs)
    
    #def toTree(self, parent):
    #    li = HTMLIntf.SubElement(parent, u"li")
    #    HTMLIntf.SubElement(li, u"a", href=u"../tables/{0}".format(self.name), title=self.description).text = self.name
        
    def select(self, sortColumn, sortDirection, moreWhere=None):
        store = self.store
        where = self.where
        args = list(
            itertools.chain(
                itertools.chain(*(column.stormArgs() for column in self.columns)),
                sortColumn.stormSortArgs()
            )
        )
        if where is None:
            where = moreWhere
        elif moreWhere is not None:
            where = And(where, moreWhere)
        if where is not None:
            args.append(where)
        resultSet = store.find(self.cls, *args)
        sortColumn.sortResultSet(resultSet, sortDirection)
        #if where is not None:
        #    resultSet = store.find(self.cls, where)
        #else:
        #    resultSet = store.find(self.cls)
        return resultSet
        

