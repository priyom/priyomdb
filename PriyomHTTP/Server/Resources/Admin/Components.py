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
from Types import Typecasts
from libPriyom.Helpers import TimeUtils
from libPriyom import Formatting
import libPriyom
from datetime import datetime, timedelta
from storm.locals import *
from storm.expr import *
from libPriyom.TransmissionParser import NodeError

Sortable = 1
Filterable = 2

class Column(object):
    def __init__(self, stormColumn, title, columnName=None, formatter=None, width=None, defaultSort=u"ASC"):
        if formatter is None:
            formatter = self.fmtNone(unicode)
        self.stormColumn = stormColumn
        self.name = columnName or self.stormColumn.name
        self.title = title
        self.formatter = formatter
        self.width = width
        self.defaultSort = defaultSort if defaultSort in (u"ASC", u"DESC") else u"ASC"
    
    @classmethod
    def ID(cls, stormClass, width="4em", **kwargs):
        return cls(getattr(stormClass, "ID"), "ID", width=width, **kwargs)
        
    @classmethod
    def Timestamp(cls, stormColumn, title, width="13em", **kwargs):
        return cls(stormColumn, title, cls.fmtNone(cls.fmtTimestamp), width=width, **kwargs)
    
    @classmethod
    def Created(cls, stormClass, defaultSort=u"DESC", **kwargs):
        return cls.Timestamp(getattr(stormClass, "Created"), "Created", defaultSort=defaultSort, **kwargs)
    
    @classmethod
    def Modified(cls, stormClass, defaultSort=u"DESC", **kwargs):
        return cls.Timestamp(getattr(stormClass, "Modified"), "Modified", defaultSort=defaultSort, **kwargs)
        
    @classmethod
    def Reference(cls, stormColumn, title, columnName, **kwargs):
        return cls(stormColumn, title, columnName=columnName, **kwargs)
        
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
    
    def _modelChanged(self, newModel):
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
        self._modelChanged(model)
    
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
        if not callable(typecast) and typecast is not None:
            raise ValueError(u"Typecast given to EditorComponent must be callable or None")
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
        # super(EditorComponent, self).editorToTree(parent)
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
        return True
    
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
        super(Input, self).editorToTree(parent)
        
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
        super(Timestamp, self).__init__(type=Input.TEXT, typecast=Typecasts.PriyomTimestamp(allowNone=allowNone, asDate=False), **kwargs)
    
    def editorToTree(self, parent):
        super(Timestamp, self).editorToTree(parent)
        dt = self.Value
        if dt is None:
            value = ""
        else:
            value = TimeUtils.toDatetime(self.Value).strftime(Formatting.priyomdate)
        self.input.set(u"value", value)
        
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
        try:
            self._value = query[self.name]
            self._foreignValue = query[self.foreignName]
            self._foreignLang = query[self.foreignLangName]
        except (ValueError, KeyError) as e:
            self.Error = unicode(e)
            return False
        return True
        
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
                enabledCall = None
                if not enabled:
                    continue
            else:
                self.hasDynamicItems = True
                enabledCall = enabled
            option = HTMLIntf.SubElement(self.reference, u"option", value=value)
            option.text = caption
            option.enabled = enabledCall
        
    def editorToTree(self, parent):
        select = self.reference.copy()
        parent.append(select)
        selectOptions = list(select) if self.hasDynamicItems else select
        for option in list(select):
            if option.enabled is not None and not option.enabled(self.Instance):
                select.remove(option)
            if option.get(u"value") == unicode(self._rawValue):
                option.set(u"selected", u"selected")
        super(Select, self).editorToTree(parent)

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
        if (id == u"" or id is None) and self.withNone is not False:
            return None
        if isinstance(id, self.stormClass) or id is None:
            return id
        condition = self.stormClass.ID == int(id)
        obj = self.store.find(self.stormClass, And(self.where, condition) if self.where is not None else condition).any()
        if obj is None:
            raise ValueError(u"ID {0} does not identify a valid {1} object.".format(int(id), self.stormClass))
        return obj
        
    def editorToTree(self, parent):
        select = HTMLIntf.SubElement(parent, u"select", attrib={
            u"name": self.name
        })
        if self.withNone is not False:
            HTMLIntf.SubElement(select, u"option", value=u"").text = self.withNone
        if self.where is not None:
            query = self.store.find(self.stormClass, self.where)
        else:
            query = self.store.find(self.stormClass)
        for item in query:
            option = HTMLIntf.SubElement(select, u"option", value=item.ID)
            option.text = unicode(item)
            if item is self.Value:
                option.set(u"selected", u"selected")
        super(SelectStormObject, self).editorToTree(parent)
                
class TextArea(EditorComponent):
    def __init__(self, rows=None, cols=None, fullWidth=False, typecast=Typecasts.NoneAsEmpty(), **kwargs):
        if cols is not None and fullWidth:
            raise ValueError(u"Cannot specify both cols= and fullWidth=True for a TextArea")
        super(TextArea, self).__init__(typecast=typecast, **kwargs)
        self.rows = int(rows) if rows is not None else None
        self.cols = int(cols) if cols is not None else None
        self.fullWidth = bool(fullWidth)
    
    def editorToTree(self, parent):
        area = HTMLIntf.SubElement(parent, u"textarea", name=self.name)
        area.text = self.Value
        if self.rows:
            area.set(u"rows", unicode(self.rows))
        if self.cols:
            area.set(u"cols", unicode(self.cols))
        elif self.fullWidth:
            wrapper = HTMLIntf.SubElement(parent, u"div", style=u"padding-right: 1em")
            parent.remove(area)
            wrapper.append(area)
            area.set(u"style", u"width: 100%")
        super(TextArea, self).editorToTree(parent)

class TransmissionContents(TextArea):
    def __init__(self, **kwargs):
        super(TransmissionContents, self).__init__(typecast=lambda x: x, **kwargs)
        
    def validate(self, query):
        self._value = " ".join((unicode(block) for block in self.Instance.blocks))
        if self.Disabled:
            return True
        if not self.name in query:
            return True
        try:
            self._value = self.checkTransmission(query[self.name])
        except (ValueError, NodeError, KeyError) as e:
            self.Error = unicode(e)
            return False
        return True
    
    def apply(self, query):
        if self.Disabled:
            return
        if not self.name in query:
            return
        self.Instance.Contents = query[self.name]
    
    def checkTransmission(self, value):
        cls = self.Instance.Class
        if cls is None:
            raise ValueError("Cannot check transmission without having a transmission class selected (you may need to save beforehand)!")
        result = cls.parsePlainText(value)
        return value

class BroadcastFrequencies(EditorComponent):
    def __init__(self, disabled=False, **kwargs):
        if disabled:
            raise ValueError("BroadcastFrequencies must not be disabled.")
        super(BroadcastFrequencies, self).__init__(typecast=None, disabled=False, **kwargs)
        self.itemPrefix = self.name + "["
        self.freqSuffix = "].Frequency"
        self.modSuffix = "].Modulation"
        self.deleteSuffix = "].Delete"
        self.updateSuffix = "].Update"
        self.newName = self.name + ".New.Value"
        self.addName = self.name + ".Add"
    
    def validate(self, query):
        # trigger rebuild of the modulation selector on each query
        self._modSelect = None
        self._newSelect = None
        
        if len(query) == 0: # no submission
            self._value = [(unicode(i), frequency.Frequency, frequency.Modulation.Name) for i, frequency in itertools.izip(itertools.count(0), self.Instance.Frequencies)]
            return True
        
        self._value = []
        preselectedKeys = (key[len(self.itemPrefix):] for key in filter((lambda key: key.find(self.itemPrefix) == 0), query.iterkeys()))
        keys = list(set((key[:key.find("]")] for key in preselectedKeys if key.find("]") >= 0)))
        
        # drop deleted entries here
        keys = [(self.itemPrefix+key+self.freqSuffix, self.itemPrefix+key+self.modSuffix) for key in keys if not self.itemPrefix+key+self.deleteSuffix in query]
        
        # thus, malformed entries are dropped silently
        items = set((libPriyom.BroadcastFrequency.parseFrequency(query[freqName]), query[modName]) for (freqName, modName) in keys if (freqName in query) and (modName in query))
        if self.addName in query and self.newName in query:
            value = query[self.newName].partition(" ")
            try:
                freq = long(value[0])
                modulation = value[2]
                if len(modulation) < 1:
                    raise ValueError("") # we catch these silently anyways
            except ValueError, TypeError:
                pass
            else:
                item = (freq, modulation)
                if item in items:
                    self.Error = u"{0}, {1} is already in the list.".format(libPriyom.BroadcastFrequency.formatFrequency(freq), modulation)
                else:
                    items.add(item)
        items = [(unicode(i), freq, mod) for (i, (freq, mod)) in itertools.izip(xrange(len(items)), items)]
        
        def sortCmp(a, b):
            v = cmp(a[1], b[1])
            return v if v != 0 else cmp(a[2], b[2])
        
        items.sort(cmp=sortCmp)
        
        if len(items) == 0:
            self.Error = u"There must be at least one frequency for each broadcast (if you found it like that in the DB: Tough luck, you have to fix this in order to manipulate this broadcast)."
            return False
        self._value = items
        return True
        
    def apply(self, query):
        for freqObj in list(self.Instance.Frequencies):
            self.store.remove(freqObj)
        for i, freq, modulation in self._value:
            libPriyom.BroadcastFrequency.fromValues(self.store, freq, modulation, self.Instance)
        
    def modSelect(self, parent, name, selected):
        select = HTMLIntf.SubElement(parent, u"select", attrib={
            u"name": name
        })
        for modulation in self.store.find(libPriyom.Modulation).order_by(Asc(libPriyom.Modulation.Name)):
            option = HTMLIntf.SubElement(select, u"option")
            option.set(u"value", modulation.Name)
            option.text = modulation.Name
            if modulation.Name == selected:
                option.set(u"selected", u"selected")
        return select
    
    def newSelect(self, parent, name):
        select = HTMLIntf.SubElement(parent, u"select", attrib={
            u"name": name
        })
        option = HTMLIntf.SubElement(select, u"option")
        option.set(u"value", u"0 AM")
        option.text = u"Select a known frequency or just add a custom one"
        knownFrequencies = self.store.using(
            libPriyom.BroadcastFrequency, 
            LeftJoin(libPriyom.Modulation, libPriyom.Modulation.ID == libPriyom.BroadcastFrequency.ModulationID), 
            LeftJoin(libPriyom.Broadcast, libPriyom.BroadcastFrequency.BroadcastID == libPriyom.Broadcast.ID)
        ).find(
            (libPriyom.BroadcastFrequency.Frequency, libPriyom.Modulation.Name), 
            libPriyom.Broadcast.StationID == self.Instance.Station.ID
        ).config(distinct=True) if self.Instance.Station is not None else None
        for frequency, modulation in knownFrequencies:
            option = HTMLIntf.SubElement(select, u"option")
            option.set(u"value", u"{0} {1}".format(frequency, modulation))
            option.text = u"{0}, {1}".format(libPriyom.BroadcastFrequency.formatFrequency(frequency), modulation)
        return select
        
    def inputToRow(self, row, item):
        td = HTMLIntf.SubElement(row, u"td")
        freqInput = HTMLIntf.SubElement(td, u"input", attrib={            
            u"name": self.itemPrefix+item[0]+self.freqSuffix,
            u"value": libPriyom.BroadcastFrequency.formatFrequency(item[1]),
        })
        
        td = HTMLIntf.SubElement(row, u"td")
        #modInput = HTMLIntf.SubElement(td, u"input", attrib={
        #    u"name": self.itemPrefix+item[0]+self.modSuffix,
        #    u"value": 
        #})
        modSelect = self.modSelect(td, self.itemPrefix+item[0]+self.modSuffix, item[2])
        
        td = HTMLIntf.SubElement(row, u"td")
        updateInput = HTMLIntf.SubElement(td, u"input", attrib={
            u"type": u"submit",
            u"name": self.itemPrefix+item[0]+self.updateSuffix,
            u"value": "Validate",
            u"class": "hidden"
        })
        deleteInput = HTMLIntf.SubElement(td, u"input", attrib={
            u"type": u"submit",
            u"name": self.itemPrefix+item[0]+self.deleteSuffix,
            u"value": u"✗"
        })
        
    def editorToTree(self, parent):
        table = HTMLIntf.SubElement(parent, u"table", attrib={
            u"class": "list fit"
        })
        colgroup = HTMLIntf.SubElement(table, u"colgroup")
        thead = HTMLIntf.SubElement(table, u"thead")
        
        HTMLIntf.SubElement(colgroup, u"col", span="1")
        HTMLIntf.SubElement(colgroup, u"col", span="1")
        HTMLIntf.SubElement(colgroup, u"col", span="1", attrib={
            u"class": u"buttons"
        })
        
        HTMLIntf.SubElement(thead, u"th").text = u"Frequency"
        HTMLIntf.SubElement(thead, u"th").text = u"Modulation"
        HTMLIntf.SubElement(thead, u"th", attrib={
            u"class": u"buttons"
        }).text = u"Act."
        
        tbody = HTMLIntf.SubElement(table, u"tbody")
        for item in self.Value:
            tr = HTMLIntf.SubElement(tbody, u"tr")
            self.inputToRow(tr, item)
        
        addDiv = HTMLIntf.SubElement(parent, u"div")
        newInput = self.newSelect(addDiv, self.newName)
        
        addInput = HTMLIntf.SubElement(addDiv, u"input", attrib={
            u"name": self.addName,
            u"type": u"submit",
            u"value": u"Add"
        })
        
        super(BroadcastFrequencies, self).editorToTree(parent)

class ParentComponent(Component):
    #def _transfer(self, src, attribs):
    #    for attrib in attribs:
    #        setattr(self, attrib, getattr(src, attrib))
    
    def __init__(self, typeCheck=None, *args, **kwargs):
        self.typeCheck = typeCheck
        if self.typeCheck is not None:
            args = [self.typeCheck(arg) for arg in args]
        else:
            args = list(args)
        self._children = args
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
    
    def __len__(self):
        return len(self._children)
    
    def __setitem__(self, key, value):
        if self.typeCheck is not None:
            value = self.typeCheck(value)
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
            
    def _instanceChanged(self, newInstance):
        super(ParentComponent, self)._instanceChanged(newInstance)
        for child in self:
            child.Instance = newInstance
    
    def append(self, item):
        if self.typeCheck is not None:
            value = self.typeCheck(value)
        item.Model = self.Model
        self._children.append(item)
    
    def extend(self, items):
        if self.typeCheck:
            items = [self.typeCheck(item) for item in items]
        for item in items:
            item.Model = self.Model
        self._children.extend(items)
    
    def insert(self, index, object):
        if self.typeCheck:
            object = self.typeCheck(object)
        object.Model = self.Model
        self._children.insert(index, object)
    
    def toTree(self, parent):
        for item in self:
            item.toTree(parent)
    
    def validate(self, query):
        valid = True
        for item in self:
            valid = item.validate(query) and valid
        return valid
    
    def apply(self, query):
        for item in self:
            item.apply(query)

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
        
        #self.stormColumns = tuple(column.stormColumn for column in self.columns)
        self.columns = tuple(self.columns)
        self.columnMap = dict(((column.name, column) for column in self.columns))
        super(VirtualTable, self).__init__(None, *args, **kwargs)
    
    #def toTree(self, parent):
    #    li = HTMLIntf.SubElement(parent, u"li")
    #    HTMLIntf.SubElement(li, u"a", href=u"../tables/{0}".format(self.name), title=self.description).text = self.name
        
    def select(self, sortColumn, sortDirection):
        store = self.store
        where = self.where
        args = list(
            itertools.chain(
                itertools.chain(*(column.stormArgs() for column in self.columns)),
                sortColumn.stormSortArgs()
            )
        )
        if where is not None:
            args.append(where)
        resultSet = store.find(self.cls, *args)
        sortColumn.sortResultSet(resultSet, sortDirection)
        #if where is not None:
        #    resultSet = store.find(self.cls, where)
        #else:
        #    resultSet = store.find(self.cls)
        return resultSet
        
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
