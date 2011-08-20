# encoding=utf-8 
from WebStack.Generic import ContentType
from Resource import Resource

class EmptyResource(Resource):
    def handle(self, trans):
        trans.set_content_type(ContentType("text/html"))
        print >>self.out, u"""
<html>
    <head>
        <title>Priyom.org API</title>
    </head>
    <body>
        <h1>Welcome!</h1>
        <h2>… to the priyom.org API server.</h2>
        <p>This is the API server which does the hard number station database work behind the curtains of <a href="http://priyom.org">priyom.org</a>.</p>
        <p>Found a malfunction? Flic over a mail to <a href="mailto:horrorcat@sotecware.net">Horrorcat</a> or check out our IRC channel <a href="irc:irc.freenode.net/#priyom">#priyom on irc.freenode.net</a>.</p>
        <p>Looking for documentation? Try <a href="doc/">this link</a>.</p>
    </body>
</html>""".encode("utf-8")
