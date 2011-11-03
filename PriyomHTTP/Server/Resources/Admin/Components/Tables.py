# encoding=utf-8

__all__ = ["TableComponent", "Table", "TableGroup", "IDTableGroup"]

from PriyomHTTP.Server.Resources import HTMLIntf
from PriyomHTTP.Server.Resources.Admin.Components.Base import Component, ParentComponent
from PriyomHTTP.Server.Resources.Admin.Components.Editors import Input, Timestamp
import itertools

class TableComponent(Component):
    def toTableRow(self, tr):
        pass
    
    def toTable(self, tbody):
        self.toTableRow(HTMLIntf.SubElement(tbody, u"tr"))
    
class TableComponentWrapper(TableComponent):
    def __init__(self, component):
        if not isinstance(component, Component):
            raise ValueError(u"Cannot wrap anything but a component subclass.")
        self.component = component
        super(TableComponentWrapper, self).__init__()
        
    def _instanceChanged(self, newInstance):
        super(TableComponentWrapper, self)._instanceChanged(newInstance)
        self.component.Instance = newInstance
    
    def _modelChanged(self, newModel):
        super(TableComponentWrapper, self)._modelChanged(newModel)
        self.component.Model = newModel
    
    def validate(self, query):
        return self.component.validate(query)
    
    def apply(self, query):
        return self.component.apply(query)
        
    def toTableRow(self, tr):
        self.component.descriptionToTree(HTMLIntf.SubElement(tr, u"th"))
        self.component.editorToTree(HTMLIntf.SubElement(tr, u"td"))
    
class Table(ParentComponent):
    def __init__(self, *args, **kwargs):
        super(Table, self).__init__(
            *itertools.chain(
                ((lambda x: x if isinstance(x, TableComponent) else TableComponentWrapper(x)),),
                args
            ), **kwargs)
        
    def toTree(self, parent):
        table = HTMLIntf.SubElement(parent, u"table", attrib={
            u"class": u"editors"
        })
        tbody = HTMLIntf.SubElement(table, u"tbody")
        for child in self:
            child.toTable(tbody)
        
class TableGroup(ParentComponent, TableComponent):
    def __init__(self, title, *args, **kwargs):
        self.title = title
        super(TableGroup, self).__init__(
            *itertools.chain(
                ((lambda x: x if isinstance(x, TableComponent) else TableComponentWrapper(x)),),
                args
            ), **kwargs)
    
    def toTable(self, tbody):
        tr = HTMLIntf.SubElement(tbody, u"tr")
        th = HTMLIntf.SubElement(tr, u"th", attrib={
            u"colspan": 2,
            u"class": "group"
        })
        th.text = self.title
        for child in self:
            child.toTable(tbody)

class IDTableGroup(TableGroup):
    def __init__(self, title, *args, **kwargs):
        super(IDTableGroup, self).__init__(title, *itertools.chain((
            Input(
                name=u"ID",
                caption=u"Database ID",
                description=u"Internal database id number",
                disabled=True
            ),
            Timestamp(
                name=u"Created",
                caption=u"Created at",
                description=u"Creation date of the database row",
                disabled=True
            ),
            Timestamp(
                name=u"Modified",
                caption=u"Last modified",
                description=u"Date of the last modification of the database row",
                disabled=True
            )
        ), args), **kwargs)

