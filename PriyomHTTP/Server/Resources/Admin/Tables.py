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
import EditRegistry
from ..HTMLResource import HTMLResource
from .. import HTMLIntf
import urllib

class AdminTablesResource(HTMLResource):
    def __init__(self, model):
        super(AdminTablesResource, self).__init__(model)
    
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
    
    def renderNavbar(self, parent):
        sec = HTMLIntf.SubElement(parent, u"section")
        HTMLIntf.SubElement(sec, u"h2").text = u"Available tables"
        ul = HTMLIntf.SubElement(sec, u"ul")
        for tableName, table in EditRegistry.virtualTables.iteritems():
            a = HTMLIntf.SubElement(HTMLIntf.SubElement(ul, u"li"), u"a", href=tableName, title=table.description)
            a.text = tableName
        
    def renderEditor(self, parent, path):
        h1 = HTMLIntf.SubElement(HTMLIntf.SubElement(parent, u"header"), u"h1")
        
        if self.table is None:
            h1.text = u"Welcome to the API table editor"
            HTMLIntf.SubElement(parent, u"p").text = u"Please select a table from the left to start editing contents."
            return
        
        if not self.table in EditRegistry.virtualTables:
            h1.text = u"""Table "{0}" not found!""".format(self.table)
            HTMLIntf.SubElement(parent, u"p").text = u"The table you are trying to access does not exist!"
            return
        
        if len(path) == 0:
            # just show the table
            virtualTable = EditRegistry.virtualTables[self.table]
            columnNames = [column.name for column in virtualTable.columns]
            h1.text = virtualTable.description
            
            orderColumn = self.getQueryValue(u"orderColumn", unicode, default=columnNames[0])
            if not orderColumn in columnNames:
                orderColumn = columnNames[0]                
            orderDirection = self.getQueryValue(u"orderDirection", unicode, default=u"ASC")
            if not orderDirection in (u"ASC", u"DESC"):
                orderDirection = u"ASC"
            offset = self.getQueryValue(u"offset", int, default=0)
            limit = 30
            
            pagesUl = HTMLIntf.SubElement(parent, u"ul", attrib={
                u"class": u"pagination"
            })
            
            table = HTMLIntf.SubElement(parent, u"table", attrib={
                u"class": u"view"
            })
            thead = HTMLIntf.SubElement(table, u"thead")
            
            HTMLIntf.SubElement(thead, u"th", attrib={
                u"class": u"buttons"
            }).text = u"Act."
            
            for column in columnNames:
                a = HTMLIntf.SubElement(HTMLIntf.SubElement(thead, u"th"), u"a")
                a.text = column
                if orderColumn != column:
                    a.set(u"href", self.buildQueryOnSameTable(orderColumn=column, orderDirection=u"ASC"))
                else:
                    if orderDirection == u"ASC":
                        a.set(u"href", self.buildQueryOnSameTable(orderColumn=column, orderDirection=u"DESC"))
                    else:
                        a.set(u"href", self.buildQueryOnSameTable(orderColumn=column, orderDirection=u"ASC"))
                        
            tbody = HTMLIntf.SubElement(table, u"tbody")
            
            resultSet = virtualTable.select()
            amount = resultSet.count()
            resultSet.order_by({
                u"ASC": Asc,
                u"DESC": Desc
            }[orderDirection](getattr(virtualTable.cls, orderColumn)))
            resultSet.config(offset=offset, limit=limit)
            # TODO: ordering
            # TODO: proper limiting!
            
            for obj in resultSet:
                tr = HTMLIntf.SubElement(tbody, u"tr")
                HTMLIntf.SubElement(HTMLIntf.SubElement(tr, u"td"), u"a", href=self.editItemHref(obj.ID), title=u"Edit / View this row in detail").text = u"[E]"
                for column in columnNames:
                    HTMLIntf.SubElement(tr, u"td").text = getattr(obj, column)
            
            #amount, = list(self.store.execute("SELECT SQL_FOUND_ROWS()"))[0]
            pages = int(amount/limit)
            if pages*limit < amount:
                pages += 1
            
            for pageNumber in xrange(1,pages+1):
                a = HTMLIntf.SubElement(HTMLIntf.SubElement(pagesUl, u"li"), u"a", href=self.buildQueryOnSameTable(orderColumn=orderColumn, orderDirection=orderDirection, offset=(pageNumber-1)*limit))
                a.text = unicode(pageNumber)
                if pageNumber == (offset/limit)+1:
                    a.set(u"class", u"current")
            
            parent.append(pagesUl.copy())
    
    def redirect(self):
        self.trans.rollback()
        path_without_query = self.trans.get_path_without_query("utf-8")
        query_string = self.trans.get_query_string()
        if query_string:
            query_string = "?" + query_string
        self.trans.redirect(self.trans.encode_path(path_without_query, "utf-8") + "/" + query_string)
        raise EndOfResponse
        
    def buildDoc(self, trans, elements):
        path = trans.get_virtual_path_info().split('/')[1:]
        if len(path) == 0:
            self.redirect()
        
        self.table = path[0]
        if not self.table:
            self.table = None
        #if self.table and not self.table in EditRegistry.virtualTables:
        #    self.notFound()
        
        self.link(u"/css/admin.css")
        
        self.navbar = HTMLIntf.SubElement(self.body, u"navbar")
        self.editor = HTMLIntf.SubElement(self.body, u"section", attrib={
            u"class": u"editor"
        })
        
        self.renderNavbar(self.navbar)
        self.renderEditor(self.editor, path[1:])
