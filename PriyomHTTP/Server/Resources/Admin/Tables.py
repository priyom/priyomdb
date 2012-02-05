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
import urllib

import PriyomHTTP.Server.HTMLIntf as HTMLIntf
from PriyomHTTP.Server.Resources.HTMLResource import HTMLResource
import UITree as UITree
from PriyomHTTP.Server.Resources.Admin.Components import Sortable, Filterable
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
        return u"?{0}".format(
            urllib.urlencode(dict)
        )
        
    def editItemHref(self, table, itemId):
        return self.getRootPath(u"{0}/{1}".format(table, itemId))
    
    def referencingTableHref(self, virtualTable, obj, referencingTable):
        return self.getRootPath(u"{0}/{1}/{2}".format(virtualTable.name, obj.ID, referencingTable.name))
    
    def renderNavbar(self, parent, path):
        sec = HTMLIntf.SubElement(parent, u"section")
        HTMLIntf.SubElement(sec, u"h2").text = u"Available tables"
        ul = HTMLIntf.SubElement(sec, u"ul")
        basePath = self.getUpwardsPath(u"", removeSegments=len(path)+1)
        for tableName, table in UITree.virtualTables.iteritems():
            href = basePath + tableName
            a = HTMLIntf.SubElement(HTMLIntf.SubElement(ul, u"li"), u"a", href=href, title=table.description)
            a.text = tableName
            
    def renderHTMLTable(self, parent, virtualTable, resultSet, orderColumn, orderDirection, offset, limit=30, allowNew=False):
        limit = 30
        
        paginationElement = HTMLIntf.SubElement(parent, u"div", attrib={
            u"class": u"button-bar pagination"
        })
        HTMLIntf.SubElement(paginationElement, u"span").text = u"Pages:"
        pagesUl = HTMLIntf.SubElement(paginationElement, u"ul")
        
        if allowNew:
            tableActions = HTMLIntf.SubElement(parent, u"div", attrib={
                u"class": u"button-bar"
            })
            HTMLIntf.SubElement(tableActions, u"span").text = u"Actions:"
            actionsUl = HTMLIntf.SubElement(tableActions, u"ul")
            new = HTMLIntf.SubElement(HTMLIntf.SubElement(actionsUl, u"li"), u"a", href=self.editItemHref(virtualTable.name, "new"), title="Create a new object")
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
            if Sortable in column:
                a = HTMLIntf.SubElement(th, u"a")
                order = HTMLIntf.SubElement(a, u"div", attrib={
                    u"class": u"order"
                })
                order.tail = column.title
            
                if orderColumn is not column:
                    a.set(u"href", self.buildQueryOnSameTable(orderColumn=column.name, orderDirection=column.defaultSort))
                else:
                    if orderDirection == u"ASC":
                        a.set(u"href", self.buildQueryOnSameTable(orderColumn=column.name, orderDirection=u"DESC"))
                        order.text = u"▲"
                    else:
                        a.set(u"href", self.buildQueryOnSameTable(orderColumn=column.name, orderDirection=u"ASC"))
                        order.text = u"▼"
            else:
                th.set(u"class", u"static")
                HTMLIntf.SubElement(th, u"div").text = column.title
            
            col = HTMLIntf.SubElement(colgroup, u"col", span="1")
            if column.width is not None:
                col.set(u"style", u"width: {0};".format(column.width))
            
        
        tbody = HTMLIntf.SubElement(table, u"tbody")
        
        amount = resultSet.count()
        if offset >= amount:
            offset = 0
        resultSet.config(offset=offset, limit=limit)
        
        for obj in resultSet:
            if not isinstance(obj, tuple):
                id = obj.ID
                obj = (obj,)
            else:
                id = obj[0].ID
            tr = HTMLIntf.SubElement(tbody, u"tr")
            actions = HTMLIntf.SubElement(tr, u"td", attrib={
                u"class": u"buttons"
            })
            HTMLIntf.SubElement(actions, u"a", href=self.editItemHref(virtualTable.name, id), title=u"Edit / View this row in detail").text = u"E"
            HTMLIntf.SubElement(actions, u"a", href=self.buildQueryOnSameTable(orderColumn=orderColumn.name, orderDirection=orderDirection, touch=id), title=u"Touch this object (set the Modified timestamp to the current time).").text = u"T"
            for column in virtualTable.columns:
                HTMLIntf.SubElement(tr, u"td").text = column.getFormattedValue(obj)
        
        pages = int(amount/limit)
        if pages*limit < amount:
            pages += 1
        
        for pageNumber in xrange(1,pages+1):
            a = HTMLIntf.SubElement(HTMLIntf.SubElement(pagesUl, u"li"), u"a", href=self.buildQueryOnSameTable(orderColumn=orderColumn.name, orderDirection=orderDirection, offset=(pageNumber-1)*limit))
            a.text = unicode(pageNumber)
            if pageNumber == (offset/limit)+1:
                a.set(u"class", u"current")
        
        parent.append(paginationElement)
        
    def renderTable(self, parent, virtualTable, h1):
        # just show the table
        h1.text = virtualTable.description
        
        orderColumn = self.getQueryValue(u"orderColumn", virtualTable.columnMap.get, default=virtualTable.columns[0])
        orderDirection = self.getQueryValue(u"orderDirection", unicode, default=u"ASC")
        if not orderDirection in (u"ASC", u"DESC"):
            orderDirection = u"ASC"
        offset = self.getQueryValue(u"offset", int, default=0)
        
        self.renderHTMLTable(parent, virtualTable, virtualTable.select(orderColumn, orderDirection), orderColumn, orderDirection, offset, allowNew=True)
    
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
                self.store.commit()
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
            
        if Store.of(obj) is not None:
            self.renderObjectNavbar(self.navbar, virtualTable, obj)
        
    def renderObjectNavbar(self, navbar, virtualTable, obj):
        if len(virtualTable.referencingTables) > 0:
            section = HTMLIntf.SubElement(navbar, u"section")
            HTMLIntf.SubElement(section, u"h2").text = u"Related table views"
            ul = HTMLIntf.SubElement(section, u"ul")
            for table in virtualTable.referencingTables:
                li = HTMLIntf.SubElement(ul, u"li")
                a = HTMLIntf.SubElement(li, u"a", href=self.referencingTableHref(virtualTable, obj, table))
                a.text = table.displayName
        
    def renderReferencedTable(self, parent, virtualTable, obj, referencingTable, referencedVirtualTable, h1):
        h1.text = u"Rows of “{1}” referencing {0}".format(unicode(obj), referencingTable.name)
        referencedVirtualTable.Model = self.model
        
        orderColumn = self.getQueryValue(u"orderColumn", referencedVirtualTable.columnMap.get, default=referencedVirtualTable.columns[0])
        orderDirection = self.getQueryValue(u"orderDirection", unicode, default=u"ASC")
        if not orderDirection in (u"ASC", u"DESC"):
            orderDirection = u"ASC"
        offset = self.getQueryValue(u"offset", int, default=0)
        
        a = HTMLIntf.SubElement(parent, u"a", href=self.editItemHref(virtualTable.name, obj.ID))
        a.text = u"Return to {0}".format(unicode(obj))
        
        self.renderHTMLTable(parent, referencedVirtualTable, referencingTable.select(referencedVirtualTable, obj, orderColumn, orderDirection), orderColumn, orderDirection, offset)
        
        self.renderObjectNavbar(self.navbar, virtualTable, obj)
        
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
            # show the table
            self.renderTable(parent, virtualTable, h1)
        elif len(path) == 1:
            # show item editor
            try:
                if path[0] == "new":
                    obj = virtualTable.cls()
                else:
                    obj = Typecasts.ValidStormObject(virtualTable.cls, self.store)(path[0])
            except:
                self.redirectUpwards()
            else:
                self.renderObjectEditor(parent, virtualTable, obj, h1)
        elif len(path) == 2:
            # show table of related objects
            if path[0] == "new":
                self.redirectUpwards()
            obj = Typecasts.ValidStormObject(virtualTable.cls, self.store)(path[0])
            try:
                referencingTable = virtualTable.referencingTableMap[path[1]]
                referencedVirtualTable = UITree.virtualTables[referencingTable.name]
            except KeyError:
                self.redirectUpwards()
            else:
                self.renderReferencedTable(parent, virtualTable, obj, referencingTable, referencedVirtualTable, h1)
    
    def redirect(self, toPath=None):
        self.trans.rollback()
        path_without_query = toPath or (self.trans.get_path_without_query("utf-8") + "/")
        query_string = self.trans.get_query_string()
        if query_string:
            query_string = "?" + query_string
        self.trans.redirect(self.trans.encode_path(path_without_query, "utf-8") + query_string)
        raise EndOfResponse
        
    def getUpwardsPath(self, append, removeSegments=2):
        path = self.trans.get_path_without_query("utf-8")
        pathSegments = path.split('/')
        pathSegments = pathSegments[:-removeSegments]
        return ("/".join(pathSegments))+"/"+append
        
    def getRootPath(self, path):
        return self.trans.get_path_without_query("utf-8")[:-len(self.trans.get_virtual_path_info("utf-8"))] + '/' + path
    
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
