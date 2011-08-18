from WebStack.Generic import ContentType
from ...APIDatabase import APIUser
from API import API


class SessionAPI(API):
    def handle(self, trans):
        super(SessionAPI, self).handle(trans)
        
        trans.set_content_type(ContentType("text/plain"))
        if (not "user" in self.query) or (not "pass" in self.query):
            print >>self.out, "failed: need user and pass arguments"
            return
        userName = self.query["user"]
        password = self.query["pass"]
        
        user = self.store.find(APIUser, APIUser.UserName == userName).any()
        if user is None:
            print >>self.out, "failed: user (%s) not found" % userName
            return
        if not user.checkPassword(password):
            print >>self.out, "failed: password invalid" % userName
            return
        password = None
        session = user.getSession()
        print >>self.out, session.Key
