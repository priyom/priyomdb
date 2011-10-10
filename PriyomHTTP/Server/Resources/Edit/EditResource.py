"""
File name: Edit.py
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
from ..HTMLResource import HTMLResource, HTMLIntf

class Editor(object):
    def __init__(self, store, name, caption, description, attribute):
        self.store = store
        self.name = name
        self.caption = caption
        self.description = description
        self.attribute = attribute
        
    def toTable(self, instance, body):
        tr = HTMLIntf.SubElement(body, u"tr")
        th = HTMLIntf.SubElement(body, u"th")
        HTMLIntf.SubElement(th, u"div", attrib={
            u"class": u"caption"
        }).text = self.caption
        HTMLIntf.SubElement(th, u"div", attrib={
            u"class": u"description"
        }).text = self.description
        
        td = HTMLIntf.SubElement(body, u"td")
        self.toCell(td)
        return tr
        
class InputEditor(Editor):
    def __init__(self, store, name, caption, description, attribute, type):
        super(InputEditor, self).__init__(store, name, caption, description, attribute)
        self.type = type
    
    def toCell(self, instance, cell):
        HTMLIntf.SubElement(cell, u"input", type=self.type, name=self.name, value=getattr(instance, self.attribute))
        
class SelectStormObjectEditor(Editor):
    def __init__(self, store, name, caption, description, attribute, cls, noneOption=False, resultSetCallback=None):
        super(InputEditor, self).__init__(store, name, caption, description, attribute)
        self.cls = cls
        self.noneOption = noneOption
        self.resultSetCallback = resultSetCallback
    
    def toCell(self, instance, cell):
        select = HTMLIntf.SubElement(cell, u"select", name=self.name)
        
        if self.noneOption:
            HTMLIntf.SubElement(cell, u"option", value=u"").text = self.noneOption
        
        objects = self.store.find(self.cls)
        if self.resultSetCallback is not None:
            objects = self.resultSetCallback(objects)
        selected = getattr(instance, self.attribute)
        for obj in objects:
            option = HTMLIntf.SubElement(select, u"option", value=unicode(obj.ID))
            option.text = unicode(obj)
            if obj is selected:
                option.set(u"selected", u"selected")

class EditorGroup(object):
    def __init__(self, caption):
        self.caption = caption
        self.editors = []
        
    def add(self, editor):
        self.editors.append(editor)
        
    def toTable(self, instance, body):
        tr = HTMLIntf.SubElement(body, u"tr")
        th = HTMLIntf.SubElement(body, u"th", colspan=u"2")
        th.text = self.caption
        
        for editor in self.editors:
            editor.toTable(instance, body)

class EditorTable(object):
    def __init__(self):
        self.editors = []
        
    def add(self, editor):
        self.editors.append(editor)
        
    def toBlock(self, instance, parent):
        table = HTMLIntf.SubElement(parent, u"table", style=u"width: 100%")
        body = HTMLIntf.SubElement(table, u"tbody")
        for editor in self.editors:
            editor.toTable(instance, body)

class EditResource(HTMLResource):
    def __init__(self, model):
        super(EditResource, self).__init__(model)
        self.editTree = self.buildEditTree()
    
    def buildEditTree(self):
        pass
    
    def buildDoc(self, trans, elements):
        self.link("/css/editor.css")
        self.link("/js/jquery.js")
        
        instance = self.getQueryValue(self.instanceParameterName, self.instanceTypecast)
        
        if "submit" in self.query:
            try:
                self.submit()
            except 
        
        form = HTMLIntf.SubElement(self.body, u"form")
        self.editTree.toBlock(instance, form)
        
        self.input(form, type=u"submit", name=u"submit", value=u"Update")
        
        
