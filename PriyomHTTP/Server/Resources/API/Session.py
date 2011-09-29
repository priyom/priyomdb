# encoding=utf-8
"""
File name: Session.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""
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
        self.allowedMethods = frozenset(["GET", "POST"])
    
    def handle(self, trans):
        trans.set_content_type(ContentType("text/plain", self.encoding))
        if (not "user" in self.query) or (not "pass" in self.query):
            if "cookie" in self.query:
                trans.set_content_type(ContentType("text/html", self.encoding))
                print >>self.out, u"""<html>
    <head>
        <title>{0}</title>
    </head>
    <body>
        <form name="login" action="getSession?cookie" method="POST">
            Username: <input type="text" name="user" value="" /><br />
            Password: <input type="password" name="pass" value="" /><br />
            <input type="submit" name="submit" value="Login" />
        </form>
    </body>
</html>""".format(
                    self.model.formatHTMLTitle(u"Login")
                ).encode(self.encoding, 'replace')
                return
            else:
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
        if "cookie" in self.query:
            trans.set_cookie_value("priyom-api-session", trans.encode_cookie_value(session.Key), '/', session.Expires)
            trans.set_content_type(ContentType("text/plain", self.encoding))
            print >>self.out, u"You are now logged in (a cookie has been set).".encode(self.encoding, 'replace')
        else:
            print >>self.out, session.Key.encode(self.encoding, 'replace')
