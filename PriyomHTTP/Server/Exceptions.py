from WebStack.Generic import ContentType, EndOfResponse
from cfg_priyomhttpd import admin, approot
import sys
import traceback
import os.path
from xml.sax.saxutils import escape

class ExceptionSelector(object):
    def __init__(self, resource, show = True):
        self.show = show
        self.resource = resource
    
    def respond(self, trans):
        try:
            self.resource.respond(trans)
        except:
            trans.rollback()
            trans.set_response_code(500)
            self.out = trans.get_response_stream()
            trans.set_content_type(ContentType("text/html"))
            
            eType, e, tb = sys.exc_info()
            
            s = u"""
<html>
    <head>
        <title>Priyom.org internal API error</title>
        <link rel="stylesheet" type="text/css" href="css/error.css"/>
    </head>
    <body>
        <h1>Internal API error</h1>"""
            if self.show:
                s += u"""
        <h2>Error information</h2>
        <dl class="exc-info">
            <dt>Exception class:</dt>
            <dd>{1}</dd>
            <dt>Message:</dt>
            <dd>{2}</dd>
        </dl>
        <h2>Stacktrace</h2>
        <p>(most recent call last)</p>
        <ul>{0}</ul>""".format(
            u"\n".join((u"""<li><div class="tb-item-head">File &quot;<span class="tb-file">{0}</span>&quot;, line <span class="tb-lineno">{1:d}</span>, in <span class="tb-func">{2}</span></div><div class="tb-item-code">{3}</div>""".format(escape(os.path.relpath(filename, approot)), lineno, escape(funcname), escape(text)) for (filename, lineno, funcname, text) in traceback.extract_tb(tb))), 
            
            escape(unicode(eType)),
            escape(unicode(e)))
                
            else:
                s += u"""
        <p>An internal error has occured. Please report this to <a href="mailto:{0}">{1}</a></p>""".format(admin["mail"], admin["name"])
            
            s += u"""
    </body>
</html>"""
            print >>self.out, s
                
