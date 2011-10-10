import HTMLIntf
import xml.etree.ElementTree as ElementTree
import itertools

class Component(object):
    def __init__(self, model):
        self.reset()
        self.model = model
        self.store = model.store
        self.priyomInterface = model.priyomInterface
        
    def reset(self):
        self._error = None
        self._instance = None
    
    def _instanceChanged(self, newInstance):
        pass
    
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

class VirtualTable(Component):
    def __init__(self, model, name=u"", description=u"", cls=None, where=None, **kwargs):
        if cls is None:
            raise ValueError(u"VirtualTable must have a class assigned")
        super(VirtualTable, self).__init__(model, **kwargs)
        self.name = name
        self.description = description
        self.cls = cls
        self.where = where
    
    def toTree(self, parent):
        li = HTMLIntf.SubElement(parent, u"li")
        HTMLIntf.SubElement(li, u"a", href=u"../tables/{0}".format(self.name), title=self.description).text = self.name
        

class EditorComponent(Component):
    def __init__(self, model, name=None, caption=None, description=u"", attributeName=None, disabled=False, typecast=unicode, **kwargs):
        super(EditorComponent, self).__init__(model, **kwargs)
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
        
    @Value.setter:
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
        if self.Disabled:
            return True
        if not self.name in query:
            return True # this is actually okay
        try:
            self._value = self.typecast(query[self.name])
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
    
    def __init__(self, model, type=InputEditor.TEXT, **kwargs):
        if not type in self.validTypes:
            raise ValueError(u"This is not a valid type for an input editor: {0!r}".format(type))
        
        super(Input, self).__init__(model, **kwargs)
        self.disabled = disabled
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
    def __init__(self, model, label=None, **kwargs):
        super(CheckBox, self).__init__(self, model, type=InputEditor.CHECKBOX, **kwargs)
        self.label = label
    
    def editorToTree(self, parent):
        super(CheckBox, self).editorToTree(parent)
        if self.label is not None:
            id = id(self)
            self.input.set(u"id", id)
            
            HTMLIntf.SubElement(parent, u"label", attrib={
                u"for": id
            }).text = self.label
            
class Select(EditorComponent):
    def __init__(self, model, items=[], **kwargs):
        if len(items) == 0:
            raise ValueError(u"Must have more than zero items for a Select.")
        super(Select, self).__init__(model, **kwargs)
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
    def __init__(self, model, virtualTable=None, stormClass=None, where=None, withMakeSingleUser=False, withEdit=False, withNone=False, **kwargs):
        if (virtualTable is None) == (stormClass is None):
            raise ValueError(u"Exactly one of (virtualTable, stormClass) must not be None. Got: ({0}, {1}).".format(virtualTable, stormClass))
        super(SelectStormObject, self).__init__(model, typecast=self.validObject, **kwargs)
        if virtualTable is not None:
            self.stormClass = virtualTable.cls
            if where is not None and virtualTable.where is not None:
                self.where = And(where, virtualTable.where)
            elif where is not None:
                self.where = where
            else:
                self.where = virtualTable.where
        else:
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
    def __init__(self, model, rows=None, cols=None, fullWidth=False, **kwargs):
        if cols is not None and fullWidth:
            raise ValueError(u"Cannot specify both cols= and fullWidth=True for a TextArea")
        super(TextArea, self).__init__(model, **kwargs)
        self.rows = int(rows)
        self.cols = int(cols)
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
    def _transfer(self, src, attribs):
        for attrib in attribs:
            setattr(self, attrib, getattr(src, attrib))
    
    def __init__(self, model, *args, typeCheck=None):
        super(ParentComponent, self).__init__(model)
        self._children = list(args)
        self.typeCheck = typeCheck
        if self.typeCheck is not None
        
        self._transfer(self._children, (
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
    
    def __setitem__(self, key, value):
        if self.typeCheck is not None:
            self.typeCheck(value)
        self._children[key] = value
    
    def append(self, item):
        if self.typeCheck is not None:
            self.typeCheck(value)
        self._children.append(item)
    
    def extend(self, items):
        if self.typeCheck:
            try:
                len(items)
            except TypeError:
                items = list(items)
            for item in items:
                self.typeCheck(items)
        self._children.extend(items)
    
    def insert(self, index, object):
        if self.typeCheck:
            self.typeCheck(object)
        self._children.insert(index, object)
        
class TableComponent(Component):
    def toTableRow(self, tr):
        pass
    
    def toTable(self, tbody):
        self.toTableRow(XHTMLIntf.SubElement(tbody, u"tr"))
    
class TableComponentWrapper(TableComponent):
    def __init__(self, component):
        if not isinstance(component, Component):
            raise ValueError(u"Cannot wrap anything but a component subclass.")
        super(TableComponentWrapper, self).__init__(component.model)
        self.component = component
        
    def toTableRow(self, tr):
        self.descriptionToTree(HTMLIntf.SubElement(tr, u"th"))
        self.editorToTree(HTMLIntf.SubElement(tr, u"td"))
    
class Table(ParentComponent):
    def __init__(self, model, *args, **kwargs):
        super(Table, self).__init__(self, model, *args, typeCheck=lambda x: x if isinstance(x, TableComponent) else TableComponentWrapper(x), **kwargs)
        
    def toTree(self, parent):
        table = HTMLIntf.SubElement(parent, u"table", attrib={
            u"class": u"editors"
        })
        tbody = HTMLIntf.SubElement(table, u"tbody")
        for child in self:
            child.toTable(tbody)
        
class TableGroup(ParentComponent, TableComponent):
    def __init__(self, model, *args, **kwargs):
        super(TableGroup, self).__init__(self, model, *args, typeCheck=lambda x: x if isinstance(x, TableComponent) else TableComponentWrapper(x), **kwargs)
    
    def toTable(self, tbody):
        for child in self:
            child.toTable(tbody)

class IDTableGroup(TableGroup):
    def __init__(self, model, *args, **kwargs):
        super(IDTableGroup, self).__init__(self, model, *itertools.chain((
            Input(
                name=u"ID",
                caption=u"Database ID",
                description=u"Internal database id number",
                disabled=True
            ),
            TimestampInput(
                name=u"Created",
                caption=u"Created at",
                description=u"Creation date of the database row",
                disabled=True
            ),
            TimestampInput(
                name=u"Modified",
                caption=u"Last modified",
                description=u"Date of the last modification of the database row",
                disabled=True
            )
        ), args), **kwargs)
