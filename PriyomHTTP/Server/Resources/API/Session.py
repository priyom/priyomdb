from WebStack.Generic import ContentType
from ...APIDatabase import APIUser
from API import API


class SessionAPI(API):
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
