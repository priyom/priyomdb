# encoding=utf-8 
"""
File name: Home.py
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
from cfg_priyomhttpd import admin
from WebStack.Generic import ContentType

import PriyomHTTP.Server.HTMLIntf as HTMLIntf
from PriyomHTTP.Server.APIDatabase import APINews
from PriyomHTTP.Server.Resources.HTMLResource import HTMLResource

class HomeResource(HTMLResource):
    technologies = [
        (u"https://fedoraproject.org/", u"Fedora Linux", u" (secured with SELinux) as server and development operating system"),
        (u"https://httpd.apache.org/", u"Apache", u" (with mod_wsgi and mod_php) for HTTP communication"),
        (u"https://www.mysql.com/", u"MySQL", u" as database server"),
        (u"http://www.phpmyadmin.net/", u"phpMyAdmin", u" for database management"),
        (u"http://www.python.org/", u"Python", u" 2.7 for all logic", [
            (u"https://storm.canonical.com/", u"Storm", u" (ORM package for Python) for database access"),
            (u"https://pypi.python.org/pypi/WebStack", u"WebStack", u" as communication layer"),
        ]),
        (u"http://www.w3.org/XML/", u"XML", u" as container format in communications"),
    ]
    
    def technologyListToTree(self, parent, node):
        ul = HTMLIntf.SubElement(parent, u"ul")
        for item in node:
            li = HTMLIntf.SubElement(ul, u"li")
            a = HTMLIntf.SubElement(li, u"a", href=item[0])
            a.text = item[1]
            a.tail = item[2]
            if len(item) == 4:
                self.technologyListToTree(li, item[3])
        return ul
    
    def buildDoc(self, trans, elements):
        self.link(u"css/home.css")
        self.setTitle(u"Priyom.org API")
        
        section = HTMLIntf.SubElement(self.body, u"section")
        HTMLIntf.SubElement(section, u"h1").text = u"Welcome!"
        HTMLIntf.SubElement(section, u"h2").text = u"… to the priyom.org API server."
        p = HTMLIntf.SubElement(section, u"p")
        p.text = u"This is the API server which does the hard number station database work behind the curtains of "
        a = HTMLIntf.SubElement(p, u"a", href=u"http://priyom.org")
        a.text = u"priyom.org"
        a.tail = u"."
            
        p = HTMLIntf.SubElement(section, u"p")
        stats = self.priyomInterface.getStatistics()
        p.text = u"Currently, we have {0} stations with {1} broadcasts and {2} transmissions, containing {4} transmission items in our database. In average, about {3} transmissions occur per broadcast and each transmission contains (in average) {5} transmission items.".format(*stats)
        
        p = HTMLIntf.SubElement(section, u"p")
        p.text = u"Found a malfunction? Flic over a mail to "
        a = HTMLIntf.SubElement(p, u"a", href=u"mailto:{0}".format(admin.get(u"mail", u"horrorcat@sotecware.net")))
        a.text = admin.get(u"name", u"Horrorcat")
        a.tail = u" or check out our IRC channel "
        a = HTMLIntf.SubElement(p, u"a", href=u"irc:irc.freenode.net/#priyom")
        a.text = u"#priyom on irc.freenode.net"
        a.tail = u"."
        
        p = HTMLIntf.SubElement(section, u"p")
        p.text = u"Looking for documentation? Try "
        a = HTMLIntf.SubElement(p, u"a", href=u"doc/")
        a.text = u"this link"
        a.tail = u"."
        
        HTMLIntf.SubElement(section, u"p").text = u"This database server is set on open-source techonolgies only:"
        self.technologyListToTree(section, self.technologies)
        
        newsSection = HTMLIntf.SubElement(section, u"section")
        HTMLIntf.SubElement(newsSection, u"h3").text = u"News / current information"
        
        table = HTMLIntf.SubElement(newsSection, u"table", attrib={
            u"class": u"news-table"
        })
        thead = HTMLIntf.SubElement(table, u"thead")
        HTMLIntf.SubElement(thead, u"th", width=u"200pt").text = u"Timestamp"
        HTMLIntf.SubElement(thead, u"th", width=u"350pt").text = u"Title"
        HTMLIntf.SubElement(thead, u"th").text = u"Contents"
        
        tbody = HTMLIntf.SubElement(table, u"tbody")
        news = self.store.find(APINews)
        news.order_by(Desc(APINews.Timestamp))
        news.config(limit=5)
        
        for item in news:
            tr = HTMLIntf.SubElement(tbody, u"tr")
            item.toTableRow(tr)
    
