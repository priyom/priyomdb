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
# encoding=utf-8 
from storm.locals import *
from ..APIDatabase import APINews
from WebStack.Generic import ContentType
from Resource import Resource

class HomeResource(Resource):
    def handle(self, trans):
        trans.set_content_type(ContentType("text/html", self.encoding))
        news = self.store.find(APINews)
        news.order_by(Desc(APINews.Timestamp))
        news.config(limit=5)
        newsRows = "\n                ".join((newsItem.html_row() for newsItem in news))
        if len(newsRows) == 0:
            newsRows = '<tr><td colspan="3">No news</td></tr>'
        print >>self.out, u"""
<html>
    <head>
        <title>Priyom.org API</title>
        <link rel="stylesheet" type="text/css" href="{0}" />
    </head>
    <body>
        <h1>Welcome!</h1>
        <h2>… to the priyom.org API server.</h2>
        <p>This is the API server which does the hard number station database work behind the curtains of <a href="http://priyom.org">priyom.org</a>.</p>
        <p>Found a malfunction? Flic over a mail to <a href="mailto:horrorcat@sotecware.net">Horrorcat</a> or check out our IRC channel <a href="irc:irc.freenode.net/#priyom">#priyom on irc.freenode.net</a>.</p>
        <p>Looking for documentation? Try <a href="doc/">this link</a>.</p>
        <p>This database server is set on open-source techonolgies only:</p>
        <ul>
            <li><a href="https://fedoraproject.org/">Fedora Linux</a> (secured with SELinux) as server and development operating system</li>
            <li><a href="https://www.archlinux.org/">ArchLinux</a> as development operating system</li>
            <li><a href="https://httpd.apache.org/">Apache</a> (with mod_wsgi and mod_php) for HTTP communication</li>
            <li><a href="https://www.mysql.com/">MySQL</a> as database server</li>
            <li><a href="http://www.phpmyadmin.net/">phpMyAdmin</a> for database management</li>
            <li><a href="http://www.python.org/">Python</a> 2.7 for all logic
            <ul>
                <li><a href="https://storm.canonical.com/">Storm</a> (ORM package for Python) for database access</li>
                <li><a href="https://pypi.python.org/pypi/WebStack">WebStack</a> as communication layer</li>
            </ul></li>
            <li><a href="http://www.w3.org/XML/">XML</a> as container format in communications</li>
            <li><a href="http://freepascal.org">FreePascal</a> as compiler for the priyom.org desktop application</li>
        </ul>
        <h3>News / current information</h3>
        <table class="news-table">
            <thead>
                <tr>
                    <th width="200pt">Timestamp</th>
                    <th width="350pt">Title</th>
                    <th>Contents</th>
                </tr>
            </thead>
            <tbody>
                {1}
            </tbody>
        </table>
    </body>
</html>""".format(
            self.model.rootPath("css/home.css"),
            newsRows
        ).encode(self.encoding, 'replace')
