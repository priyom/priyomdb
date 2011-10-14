# encoding=utf-8
"""
File name: Components.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""
from .. import HTMLIntf
from ...WebModel import WebModel
import xml.etree.ElementTree as ElementTree
import itertools

class Component(object):
    def __init__(self, model=None, **kwargs):
        #super(Component, self).__init__(**kwargs)
        self.reset()
        self.Model = model
        
    def reset(self):
        self._error = None
        self._instance = None
    
    def _instanceChanged(self, newInstance):
        pass
        
    @property
    def Model(self):
        return self.model
    
    @Model.setter
    def Model(self, model):
        self.model = model
        if model is not None:
            self.store = model.store
            self.priyomInterface = model.priyomInterface
    
    @property
    def Instance(self):
        return self._instance
    
    @Instance.setter
    def Instance(self, value):
        self.reset()
        self._instance = value
        self._instanceChanged(value)
        
    @property
    def Error(self):
        return self._error
    
    @Error.setter
    def Error(self, value):
        self._error = value
        
    def validate(self, query):
        return True
    
    def apply(self, query):
        pass
        
    def toTree(self, parent):
        pass

class EditorComponent(Component):
    def __init__(self, name=None, caption=None, description=u"", attributeName=None, disabled=False, typecast=unicode, **kwargs):
        super(EditorComponent, self).__init__(**kwargs)
        if name is None:
            raise ValueError(u"EditorComponent name must not be None")
        if not callable(typecast):
            raise ValueError(u"Typecast given to EditorComponent must be callable")
        self.name = name
        self.caption = caption or name
        self.attributeName = attributeName or name
        self.description = description
        self.typecast = typecast
        self._disabled = disabled
        
    def reset(self):
        super(EditorComponent, self).reset()
        self._value = None
        
    @property
    def Value(self):
        if self._instance is None:
            raise ValueError(u"Cannot get value without an instance assigned.")
        return self._value
        
    @Value.setter
    def Value(self, value):
        self._value = self.typecast(value)
        self._rawValue = value
        
    @property
    def Disabled(self):
        if callable(self._disabled):
            return self._disabled(self.Instance)
        else:
            return self._disabled
        
    def descriptionToTree(self, parent):
        HTMLIntf.SubElement(parent, u"p", attrib={
            u"class": u"caption"
        }).text = self.caption
        if self.description is not None:
            HTMLIntf.SubElement(parent, u"p", attrib={
                u"class": u"description"
            }).text = self.description
    
    def editorToTree(self, parent):
        super(EditorComponent, self).__init__(parent)
        if self.Error is not None:
            div = HTMLIntf.SubElement(parent, u"div", attrib={
                u"class": u"error"
            })
            if type(self.Error) == ElementTree.Element:
                div.append(self.Error)
            else:
                div.text = unicode(self.Error)
                
    def validate(self, query):
        self.Value = getattr(self._instance, self.attributeName)
        if self.Disabled:
            return True
        if not self.name in query:
            return True # this is actually okay
        try:
            self.Value = query[self.name]
        except (ValueError, TypeError) as e:
            self.Error = unicode(e)
            return False
            
    def apply(self, query):
        if self.Disabled:
            return
        if not self.name in query:
            return
        setattr(self.Instance, self.attributeName, self.Value)
        
    def toTree(self, parent):
        self.descriptionToTree(HTMLIntf.SubElement(parent, u"div", attrib={
            u"class": u"edit-description"
        }))
        self.editorToTree(HTMLIntf.SubElement(parent, u"div", attrib={
            u"class": u"edit-editor"
        }))

class Input(EditorComponent):
    TEXT = u"text"
    PASSWORD = u"password"
    CHECKBOX = u"checkbox"
    
    validTypes = [TEXT, PASSWORD, CHECKBOX]
    
    def __init__(self, type=TEXT, **kwargs):
        if not type in self.validTypes:
            raise ValueError(u"This is not a valid type for an input editor: {0!r}".format(type))
        
        super(Input, self).__init__(**kwargs)
        self.type = type
    
    def editorToTree(self, parent):
        self.input = HTMLIntf.SubElement(parent, u"input", attrib={
            u"type": self.type,
            u"name": self.name,
            u"value": self.Value
        })
        if self.Disabled:
            self.input.set(u"disabled", u"disabled")
        super(Input, self).__init__(parent)
        
class CheckBox(Input):
    def __init__(self, label=None, **kwargs):
        super(CheckBox, self).__init__(type=Input.CHECKBOX, **kwargs)
        self.label = label
    
    def editorToTree(self, parent):
        super(CheckBox, self).editorToTree(parent)
        if self.label is not None:
            id = id(self)
            self.input.set(u"id", id)
            
            HTMLIntf.SubElement(parent, u"label", attrib={
                u"for": id
            }).text = self.label

class Timestamp(Input):
    def __init__(self, allowNone=False, **kwargs):
        super(Timestamp, self).__init__(type=Input.TEXT, typecast=WebModel.PriyomTimestamp(allowNone=allowNone, asDate=False), **kwargs)
    
    def editorToTree(self, parent):
        super(Timestamp, self).editorToTree(parent)
        self.input.set(u"value", TimeUtils.toDatetime(self.Value).strftime(Formatting.priyomdate))
        
class ForeignInput(Input):
    def __init__(self, foreignName=None, foreignLangName=None, foreignAttribute=None, **kwargs):
        if not foreignName:
            raise ValueError(u"Need a proper foreign name at least. Got: {0}".format(foreignName))
        super(ForeignInput, self).__init__(type=Input.TEXT, **kwargs)
        self.foreignName = foreignName
        self.foreignLangName = foreignLangName or foreignName + u"Lang"
        self.foreignAttribute = foreignAttribute or foreignName
        
    def validate(self, query):
        self._value = getattr(self._instance, self.attributeName)
        helper = getattr(self._instance, self.foreignAttribute)
        self._foreignValue = helper.Value
        self._foreignLang = helper.LangCode
        if self.Disabled:
            return True
        if not self.name in query or not self.foreignName in query or not self.foreignLangName:
            return True
        self._value = query[self.name]
        self._foreignValue = query[self.foreignName]
        self._foreignLang = query[self.foreignLangName]
        
    def apply(self, query):
        if self.Disabled:
            return
        if not self.name in query or not self.foreignName in query or not self.foreignLangName:
            return
        setattr(self._instance, self.attributeName, self._value)
        if self._foreignValue and self._foreignLang:
            helper = getattr(self._instance, self.foreignAttribute)
            helper.Value = self._foreignValue
            helper.LangCode = self._foreignLang
        
    def editorToTree(self, parent):
        super(ForeignInput, self).editorToTree(parent)
        HTMLIntf.SubElement(parent, u"br").tail = u"Foreign data (langcode / contents): "
        HTMLIntf.SubElement(parent, u"input", attrib={
            u"name": self.foreignLangName,
            u"type": u"text",
            u"value": self._foreignLang
        }).tail = u" / "
        HTMLIntf.SubElement(parent, u"input", attrib={
            u"name": self.foreignName,
            u"type": u"text",
            u"value": self._foreignValue
        })

class Select(EditorComponent):
    def __init__(self, items=[], **kwargs):
        if len(items) == 0:
            raise ValueError(u"Must have more than zero items for a Select.")
        super(Select, self).__init__(**kwargs)
        self.items = items
        self.hasDynamicItems = False
        self.reference = HTMLIntf.Element(u"select", name=self.name)
        for value, caption, enabled in self.items:
            if not callable(enabled):
                enabled = None
                if not enabled:
                    continue
            else:
                self.hasDynamicItems = True
            option = HTMLIntf.SubElement(self.reference, u"option", value=value)
            option.text = caption
            option.enabled = enabled
        
    def editorToTree(self, parent):
        select = self.reference.copy()
        parent.append(select)
        selectOptions = list(select) if self.hasDynamicItems else select
        for option in list(select):
            if option.enabled is not None and not option.enabled(self.Instane):
                select.remove(option)
            if option.get(u"value") == unicode(self._rawValue):
                option.set(u"selected", u"selected")

class SelectStormObject(EditorComponent):
    def __init__(self, stormClass=None, where=None, withMakeSingleUser=False, withEdit=False, withNone=False, **kwargs):
        #if (virtualTable is None) == (stormClass is None):
        #    raise ValueError(u"Exactly one of (virtualTable, stormClass) must not be None. Got: ({0}, {1}).".format(virtualTable, stormClass))
        super(SelectStormObject, self).__init__(typecast=self.validObject, **kwargs)
        #if virtualTable is not None:
        #    self.stormClass = virtualTable.cls
        #    if where is not None and virtualTable.where is not None:
        #        self.where = And(where, virtualTable.where)
        #    elif where is not None:
        #        self.where = where
        #    else:
        #        self.where = virtualTable.where
        #else:
        self.stormClass = stormClass
        self.where = where
        self.withMakeSingleUser = withMakeSingleUser
        self.withEdit = withEdit
        self.withNone = withNone
        
    def validObject(self, id):
        if id == u"" and self.withNone is not False:
            return None
        obj = self.store.find(self.stormClass, And(where, self.stormClass.ID == int(id))).any()
        if obj is None:
            raise ValueError(u"ID {0} does not identify a valid {1} object.".format(int(id), self.stormClass))
        return obj
        
    def editorToTree(self, parent):
        select = HTMLIntf.SubElement(parent, u"select", attrib={
            u"name": self.name
        })
        if self.withNone is not False:
            HTMLIntf.SubElement(select, u"option", value=u"").text = self.withNone
        for item in self.store.find(self.stormClass, where):
            option = HTMLIntf.SubElement(select, u"option", value=item.ID)
            option.text = unicode(item)
            if item is self.Value:
                option.set(u"selected", u"selected")
                
class TextArea(EditorComponent):
    def __init__(self, rows=None, cols=None, fullWidth=False, **kwargs):
        if cols is not None and fullWidth:
            raise ValueError(u"Cannot specify both cols= and fullWidth=True for a TextArea")
        super(TextArea, self).__init__(**kwargs)
        self.rows = int(rows) if rows is not None else None
        self.cols = int(cols) if cols is not None else None
        self.fullWidth = bool(fullWidth)
    
    def editorToTree(self, parent):
        area = HTMLIntf.SubElement(parent, u"textarea", name=self.name)
        if self.rows:
            area.set(u"rows", unicode(self.rows))
        if self.cols:
            area.set(u"cols", unicode(self.cols))
        elif self.fullWidth:
            wrapper = HTMLIntf.SubElement(parent, u"div", style=u"padding-right: 1em")
            parent.remove(area)
            wrapper.append(area)
            area.set(u"style", u"width: 100%")
        area.text = self.Value

class ParentComponent(Component):
    #def _transfer(self, src, attribs):
    #    for attrib in attribs:
    #        setattr(self, attrib, getattr(src, attrib))
    
    def __init__(self, typeCheck=None, *args, **kwargs):
        self.typeCheck = typeCheck
        if self.typeCheck is not None:
            for item in args:
                self.typeCheck(item)
        self._children = list(args)
        """self._transfer(self._children, (
            "__getitem__",
            "__getslice__",
            "__len__",
            "__iter__",
            "__delitem__",
            "__contains__",
            "__reduce__",
            "__reversed__",
            "count",
            "index",
            "pop",
            "remove",
            "reverse",
            "sort"
        ))
        print(dir(self))
        print(self.__iter__)"""
        super(ParentComponent, self).__init__(**kwargs)
    
    def __iter__(self):
        return iter(self._children)
    
    def __setitem__(self, key, value):
        if self.typeCheck is not None:
            self.typeCheck(value)
        value.Model = self.Model
        self._children[key] = value
        
    @property
    def Model(self):
        return self.model
        
    @Model.setter
    def Model(self, model):
        self.model = model
        if model is not None:
            self.store = model.store
            self.priyomInterface = model.priyomInterface
        for child in self:
            child.Model = model
    
    def append(self, item):
        if self.typeCheck is not None:
            self.typeCheck(value)
        item.Model = self.Model
        self._children.append(item)
    
    def extend(self, items):
        try:
            len(items)
        except TypeError:
            items = list(items)
        if self.typeCheck:
            for item in items:
                self.typeCheck(items)
                item.Model = self.Model
        else:
            for item in items:
                item.Model = self.Model
        self._children.extend(items)
    
    def insert(self, index, object):
        if self.typeCheck:
            self.typeCheck(object)
        object.Model = self.Model
        self._children.insert(index, object)

class VirtualTable(ParentComponent):
    def __init__(self, name, cls, *args, **kwargs):
        if cls is None:
            raise ValueError(u"VirtualTable must have a class assigned")
        self.description = kwargs.get(u"description", u"")
        self.where = kwargs.get(u"where", None)
        self.columns = kwargs.get(u"columns", [])
        self.name = name
        self.cls = cls
        if len(self.columns) == 0:
            raise ValueError(u"Must have a list of columns")
        
        if type(self.columns[0]) == unicode or type(self.columns[0]) == str:
            self.columns = tuple((getattr(self.cls, column) for column in self.columns))
        else:
            self.columns = tuple(self.columns)
        
        super(VirtualTable, self).__init__(*args, **kwargs)
    
    def toTree(self, parent):
        li = HTMLIntf.SubElement(parent, u"li")
        HTMLIntf.SubElement(li, u"a", href=u"../tables/{0}".format(self.name), title=self.description).text = self.name
        
    def select(self):
        store = self.store
        where = self.where
        if where is not None:
            resultSet = store.find(self.cls, where)
        else:
            resultSet = store.find(self.cls)
        return resultSet
        
class TableComponent(Component):
    def toTableRow(self, tr):
        pass
    
    def toTable(self, tbody):
        self.toTableRow(XHTMLIntf.SubElement(tbody, u"tr"))
    
class TableComponentWrapper(TableComponent):
    def __init__(self, component):
        print(type(component))
        if not isinstance(component, Component):
            raise ValueError(u"Cannot wrap anything but a component subclass.")
        super(TableComponentWrapper, self).__init__(component.model)
        self.component = component
        
    def toTableRow(self, tr):
        self.descriptionToTree(HTMLIntf.SubElement(tr, u"th"))
        self.editorToTree(HTMLIntf.SubElement(tr, u"td"))
    
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
        th = HTMLIntf.SubElement(tr, u"th", colspan=2)
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
