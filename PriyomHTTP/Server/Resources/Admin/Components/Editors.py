# encoding=utf-8

__all__ = ["BroadcastFrequencies", "CheckBox", "ForeignInput", "Input", "Select", "SelectStormObject", "TextArea", "Timestamp", "TransmissionContents"]

from storm.locals import *
from storm.expr import *
import itertools
from Types import Typecasts
import libPriyom
from libPriyom import Formatting
from libPriyom.Helpers import TimeUtils
from PriyomHTTP.Server.Resources import HTMLIntf
from PriyomHTTP.Server.Resources.Admin.Components.Base import EditorComponent

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

            
