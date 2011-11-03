# encoding=utf-8
"""
File name: Tables.py
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
from storm.locals import *
from WebStack.Generic import ContentType, EndOfResponse
import UITree
from ..HTMLResource import HTMLResource
from .. import HTMLIntf
import urllib
from Types import Typecasts

class AdminTablesResource(HTMLResource):
    def __init__(self, model):
        super(AdminTablesResource, self).__init__(model)
        self.allowedMethods = frozenset(("GET", "POST"))
    
    def notFound(self):
        #self.trans.rollback()
        self.trans.set_response_code(404)
        #self.trans.set_content_type(ContentType("text/plain", self.encoding))
        #print >>self.out, )
        #raise EndOfResponse
        HTMLIntf.SubElement(self.body, u"p").text = u"Table not found: \"{1}\"".format(self.trans.get_processed_virtual_path_info(), self.trans.get_virtual_path_info())
        
    def buildQueryOnSameTable(self, **dict):
        return u"{0}?{1}".format(
            self.table, 
            urllib.urlencode(dict)
        )
        
    def editItemHref(self, itemId, table=None):
        return u"{0}/{1}".format(
            table or self.table,
            itemId
        )
    
    def renderNavbar(self, parent, path):
        sec = HTMLIntf.SubElement(parent, u"section")
        HTMLIntf.SubElement(sec, u"h2").text = u"Available tables"
        ul = HTMLIntf.SubElement(sec, u"ul")
        basePath = self.getUpwardsPath(u"", removeSegments=len(path)+1)
        for tableName, table in UITree.virtualTables.iteritems():
            href = basePath + tableName
            a = HTMLIntf.SubElement(HTMLIntf.SubElement(ul, u"li"), u"a", href=href, title=table.description)
            a.text = tableName
            
    def renderTable(self, parent, virtualTable, h1):
        # just show the table
        h1.text = virtualTable.description
        
        orderColumn = self.getQueryValue(u"orderColumn", virtualTable.columnMap.get, default=virtualTable.columns[0])
        orderDirection = self.getQueryValue(u"orderDirection", unicode, default=u"ASC")
        if not orderDirection in (u"ASC", u"DESC"):
            orderDirection = u"ASC"
        offset = self.getQueryValue(u"offset", int, default=0)
        limit = 30
        
        paginationElement = HTMLIntf.SubElement(parent, u"div", attrib={
            u"class": u"button-bar pagination"
        })
        HTMLIntf.SubElement(paginationElement, u"span").text = u"Pages:"
        pagesUl = HTMLIntf.SubElement(paginationElement, u"ul")
        
        tableActions = HTMLIntf.SubElement(parent, u"div", attrib={
            u"class": u"button-bar"
        })
        HTMLIntf.SubElement(tableActions, u"span").text = u"Actions:"
        actionsUl = HTMLIntf.SubElement(tableActions, u"ul")
        new = HTMLIntf.SubElement(HTMLIntf.SubElement(actionsUl, u"li"), u"a", href=self.editItemHref("new"), title="Create a new object")
        new.text = u"New"
        
        table = HTMLIntf.SubElement(parent, u"table", attrib={
            u"class": u"list view"
        })
        colgroup = HTMLIntf.SubElement(table, u"colgroup")
        thead = HTMLIntf.SubElement(table, u"thead")
        
        HTMLIntf.SubElement(thead, u"th", attrib={
            u"class": u"buttons"
        }).text = u"Act."
        HTMLIntf.SubElement(colgroup, u"col", span="1").set("style", "width: 8em;")
        
        
        for column in virtualTable.columns:
            th = HTMLIntf.SubElement(thead, u"th")
            col = HTMLIntf.SubElement(colgroup, u"col", span="1")
            if column.width is not None:
                col.set(u"style", u"width: {0};".format(column.width))
            a = HTMLIntf.SubElement(th, u"a")
            a.text = column.title
            columnName = column.stormColumn.name
            if orderColumn is not column:
                a.set(u"href", self.buildQueryOnSameTable(orderColumn=columnName, orderDirection=column.defaultSort))
            else:
                divOrder = HTMLIntf.Element(u"div", attrib={
                    u"class": "order"
                })
                #th.insert(0, divOrder)
                divOrder.tail = a.text
                a.text = u""
                a.append(divOrder)
                if orderDirection == u"ASC":
                    a.set(u"href", self.buildQueryOnSameTable(orderColumn=columnName, orderDirection=u"DESC"))
                    divOrder.text = u"▲"
                else:
                    a.set(u"href", self.buildQueryOnSameTable(orderColumn=columnName, orderDirection=u"ASC"))
                    divOrder.text = u"▼"
                    
        tbody = HTMLIntf.SubElement(table, u"tbody")
        
        resultSet = virtualTable.select()
        amount = resultSet.count()
        resultSet.order_by({
            u"ASC": Asc,
            u"DESC": Desc
        }[orderDirection](orderColumn.stormColumn))
        resultSet.config(offset=offset, limit=limit)
        # TODO: ordering
        # TODO: proper limiting!
        
        for obj in resultSet:
            tr = HTMLIntf.SubElement(tbody, u"tr")
            actions = HTMLIntf.SubElement(tr, u"td", attrib={
                u"class": u"buttons"
            })
            HTMLIntf.SubElement(actions, u"a", href=self.editItemHref(obj.ID), title=u"Edit / View this row in detail").text = u"E"
            HTMLIntf.SubElement(actions, u"a", href=self.buildQueryOnSameTable(orderColumn=orderColumn, orderDirection=orderDirection, touch=obj.ID), title=u"Touch this object (set the Modified timestamp to the current time).").text = u"T"
            for column in virtualTable.columns:
                HTMLIntf.SubElement(tr, u"td").text = column.formatter(getattr(obj, column.stormColumn.name))
        
        #amount, = list(self.store.execute("SELECT SQL_FOUND_ROWS()"))[0]
        pages = int(amount/limit)
        if pages*limit < amount:
            pages += 1
        
        for pageNumber in xrange(1,pages+1):
            a = HTMLIntf.SubElement(HTMLIntf.SubElement(pagesUl, u"li"), u"a", href=self.buildQueryOnSameTable(orderColumn=orderColumn.stormColumn.name, orderDirection=orderDirection, offset=(pageNumber-1)*limit))
            a.text = unicode(pageNumber)
            if pageNumber == (offset/limit)+1:
                a.set(u"class", u"current")
        
        parent.append(paginationElement.copy())
    
    def renderObjectEditor(self, parent, virtualTable, obj, h1):
        virtualTable.Model = self.model
        virtualTable.Instance = obj
        validated = virtualTable.validate(self.postQuery)
        
        form = HTMLIntf.SubElement(parent, u"form", method="POST", name="editor")
        virtualTable.toTree(form)
        validate = HTMLIntf.SubElement(form, u"input", name="submit", value="Validate", type="submit")
        if "submit" in self.query and validated:
            if self.query["submit"] == "Save":
                if Store.of(obj) is None:
                    self.store.add(obj)
                    isNew = True
                else:
                    isNew = False
                virtualTable.apply(self.query)
                obj.touch()
                self.store.flush()
                self.store.invalidate(obj)
                if isNew:
                    self.redirect(self.getUpwardsPath(unicode(obj.ID), 1))
            HTMLIntf.SubElement(form, u"input", name="submit", value="Save", type="submit")
        else:
            validate.tail = u" Please check your input."
        if Store.of(obj) is None:
            h1.text = u"Add new object"
        else:
            h1.text = u"Editing: {0}".format(unicode(obj))
        
    def renderEditor(self, parent, path):
        h1 = HTMLIntf.SubElement(HTMLIntf.SubElement(parent, u"header"), u"h1")
        
        if self.table is None:
            h1.text = u"Welcome to the API table editor"
            HTMLIntf.SubElement(parent, u"p").text = u"Please select a table from the left to start editing contents."
            return
        
        if not self.table in UITree.virtualTables:
            h1.text = u"""Table "{0}" not found!""".format(self.table)
            HTMLIntf.SubElement(parent, u"p").text = u"The table you are trying to access does not exist!"
            return
        
        virtualTable = UITree.virtualTables[self.table]
        if len(path) == 0:
            self.renderTable(parent, virtualTable, h1)
        elif len(path) == 1:
            try:
                if path[0] == "new":
                    obj = virtualTable.cls()
                else:
                    obj = Typecasts.ValidStormObject(virtualTable.cls, self.store)(path[0])
            except:
                self.redirectUpwards()
            else:
                self.renderObjectEditor(parent, virtualTable, obj, h1)
    
    def redirect(self, toPath=None):
        self.trans.rollback()
        path_without_query = toPath or (self.trans.get_path_without_query("utf-8") + "/")
        query_string = self.trans.get_query_string()
        if query_string:
            query_string = "?" + query_string
        self.trans.redirect(self.trans.encode_path(toPath, "utf-8") + query_string)
        raise EndOfResponse
        
    def getUpwardsPath(self, append, removeSegments=2):
        path = self.trans.get_path_without_query("utf-8")
        pathSegments = path.split('/')
        pathSegments = pathSegments[:-removeSegments]
        return ("/".join(pathSegments))+"/"+append
    
    def redirectUpwards(self):
        self.trans.rollback()
        path_without_query = self.trans.get_path_without_query("utf-8")
        query_string = self.trans.get_query_string()
        pathSegments = path_without_query.split('/')
        if pathSegments[-1] == "":
            pathSegments = pathSegments[:-2]
        else:
            pathSegments = pathSegments[:-1]
        newPath = "/".join(pathSegments)
        if query_string:
            query_string = "?" + query_string
        self.trans.redirect(self.trans.encode_path(newPath, "utf-8") + query_string)
        raise EndOfResponse
        
    def buildDoc(self, trans, elements):
        path = trans.get_virtual_path_info().split('/')[1:]
        if len(path) == 0:
            self.redirect()
        
        self.table = path[0]
        if not self.table:
            self.table = None
        #if self.table and not self.table in UITree.virtualTables:
        #    self.notFound()
        
        self.link(u"/css/admin.css")
        
        self.navbar = HTMLIntf.SubElement(self.body, u"navbar")
        self.editor = HTMLIntf.SubElement(self.body, u"section", attrib={
            u"class": u"editor"
        })
        
        self.renderNavbar(self.navbar, path[1:])
        self.renderEditor(self.editor, path[1:])
