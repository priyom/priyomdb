"""
File name: Base.py
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
__all__ = ["Component", "EditorComponent", "ParentComponent"]

import xml.etree.ElementTree as ElementTree
import PriyomHTTP.Server.HTMLIntf as HTMLIntf

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

