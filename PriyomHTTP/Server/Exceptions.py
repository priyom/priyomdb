from WebStack.Generic import ContentType, EndOfResponse
from cfg_priyomhttpd import admin
import sys
import traceback

class ExceptionSelector(object):
    def __init__(self, resource, show = True):
        self.show = show
        self.resource = resource
    
    def respond(self, trans):
        try:
            return self.resource.respond(trans)
        except:
            trans.rollback()
            trans.set_response_code(500)
            self.out = trans.get_response_stream()
            trans.set_content_type(ContentType("text/html"))
            
            eType, e, tb = sys.exc_info()
            
            s = """
<html>
    <head>
        <title>Priyom.org internal API error</title>
    </head>
    <body>
        <h1>Internal API error</h1>"""
            if self.show:
                s += """
        <h2>Stacktrace</h2>
        <p>(most recent call last)</p>
        <ul>{0}</ul>""".format("\n".join(("""<li><p>File "<b>{0}</b>", line <b>{1:d}</b>, in <b>{2}</b><br/><pre>{3}</pre></p>""".format(filename, lineno, funcname, text) for (filename, lineno, funcname, text) in traceback.extract_tb(tb))))
                
            else:
                s += """
        <p>An internal error has occured. Please report this to <a href="mailto:{0}">{1}</a></p>""".format(admin["mail"], admin["name"])
            
            s += """
    </body>
</html>"""
            print >>self.out, s
                
