from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class ImportAPI(API):
    def handle(self, trans):
        if trans.get_request_method() == "GET":
            trans.set_content_type(ContentType("text/plain"))
            print >>self.out, "POST your transaction data either as application/xml or as application/json according to priyom.org transaction specification"
            return
        if trans.get_request_method() != "POST":
            trans.set_response_code(400)
            return
            
        
        contentType = str(trans.get_content_type()).split(' ', 1)[0].split(';', 1)[0]
        try:
            method = {
                "application/xml": self.model.importFromXmlStr,
                "application/json": self.model.importFromJsonStr
            }[contentType]
        except KeyError:
            trans.set_response_code(400)
            raise EndOfResponse
        data = trans.get_request_stream().read()
        context = method(data)
        trans.set_content_type(ContentType("text/plain"))
        print >>self.out, context.log.get()
