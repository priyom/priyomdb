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
        <p>This database server is set on open-source techonolgies only:</p>
        <ul>
            <li><a href="https://fedoraproject.org/">Fedora Linux</a> (secured with SELinux) as server and development operating system</li>
            <li><a href="https://www.archlinux.org/">ArchLinux</a> as development operating system</li>
            <li><a href="https://httpd.apache.org/">Apache</a> (with mod_python) for HTTP communication</li>
            <li><a href="https://www.mysql.com/">MySQL</a> for database server</li>
            <li><a href="http://www.python.org/">Python</a> 2.7 for all logic</li>
            <li><a href="https://storm.canonical.com/">Storm</a> (ORM package for Python) for database access</li>
            <li><a href="https://pypi.python.org/pypi/WebStack">WebStack</a> as communication layer</li>
            <li><a href="http://www.w3.org/XML/">XML</a> as container format in communications</li>
            <li><a href="http://www.json.org/>JSON</a> planned as future container format if any need exists</li>
            <li><a href="http://freepascal.org">FreePascal</a> as compiler for the priyom.org desktop application</li>
        </ul>
    </body>
</html>""".encode("utf-8")
