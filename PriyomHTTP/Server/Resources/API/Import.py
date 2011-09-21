from WebStack.Generic import ContentType
from libPriyom import *
from API import API

class ImportAPI(API):
    title = u"import"
    shortDescription = u"Import a priyom transaction xml into the database"
    
    docArgs = []
    docCallSyntax = u""
    docRemarks = u"Must be called in POST mode, the transaction must be sent as request body with Content-Type set to application/xml."
    docRequiredPrivilegues = u"transaction"
    
    def __init__(self, model):
        super(ImportAPI, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
    
    def handle(self, trans):
        if trans.get_request_method() == "GET":
            trans.set_response_code(405)
            trans.set_header_value("Allow", "POST")
            trans.set_content_type(ContentType("text/plain"))
            print >>self.out, "POST your transaction data either as application/xml or as application/json according to priyom.org transaction specification"
            return
        trans.set_content_type(ContentType("text/plain". self.encoding))
        
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
        print >>self.out, context.log.get()
