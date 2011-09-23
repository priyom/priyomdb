from WebStack.Generic import ContentType, EndOfResponse
from Resource import Resource
from libPriyom import *

class SubmitLogResource(Resource):
    def __init__(self, model):
        super(SubmitLogResource, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
    
    def handle(self, trans):
        trans.set_content_type(ContentType("text/html", self.encoding))
        
        print >>self.out, u"""<html>
    <head>
        <title>Submit logs</title>
    </head>
    <body>
    
    </body>
</html>""".encode(self.encoding)
