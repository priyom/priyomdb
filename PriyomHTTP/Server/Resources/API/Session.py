# encoding=utf-8
from WebStack.Generic import ContentType
from ...APIDatabase import APIUser
from API import API, CallSyntax, Argument


class SessionAPI(API):
    title = u"getSession"
    shortDescription = u"Login and get a session id"
    
    docArgs = [
        Argument(u"user", u"string", u"user name", metavar=u"username"),
        Argument(u"pass", u"string", u"password", metavar=u"password")
    ]
    docCallSyntax = CallSyntax(docArgs, u"?{0}&{1}")
    docReturnValue = u"Returns the session id on success or “failed: message” in case of an error, whereas message will be replaced by the error message."
    
    def __init__(self, model):
        super(SessionAPI, self).__init__(model)
        self.allowedMethods = frozenset(["GET"])
    
    def handle(self, trans):
        trans.set_content_type(ContentType("text/plain", self.encoding))
        if (not "user" in self.query) or (not "pass" in self.query):
            print >>self.out, (u"failed: need user and pass arguments").encode(self.encoding)
            return
        userName = self.query["user"]
        password = self.query["pass"]
        
        user = self.store.find(APIUser, APIUser.UserName == userName).any()
        if user is None:
            print >>self.out, (u"failed: user (%s) not found" % userName).encode(self.encoding)
            return
        if not user.checkPassword(password):
            print >>self.out, (u"failed: password invalid").encode(self.encoding)
            return
        password = None
        session = user.getSession()
        print >>self.out, session.Key.encode(self.encoding)
