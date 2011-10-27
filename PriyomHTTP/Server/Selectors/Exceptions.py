"""
File name: Exceptions.py
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
from WebStack.Generic import ContentType, EndOfResponse
from WebStack.Helpers.Request import Cookie, HeaderDict, HeaderValue
from cfg_priyomhttpd import application, admin, errors
import sys
import traceback
import os.path
from xml.sax.saxutils import escape

from libPriyom.Helpers import TimeUtils
import email, smtplib
from email.message import Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class ExceptionSelector(object):
    def __init__(self, resource, model):
        self.show = errors["show"]
        self.resource = resource
        self.model = model
        
    def fancyRepr(self, obj, indent=u""):
        newIndent = indent+u"    "
        newIndent2 = indent+u"        "
        if type(obj) == dict:
            items = obj.items()
            if len(items) == 0:
                return u"{}"
            return u"{\n"+newIndent+((u"\n"+newIndent).join(
                u"{0}: {1}".format(self.fancyRepr(key, newIndent2), self.fancyRepr(value, indent+u"        ")) for key, value in obj.items()
            ))+u"\n"+indent+u"}"
        elif type(obj) == list:
            if len(obj) == 0:
                return u"[]"
            return u"[\n"+newIndent+((u"\n"+newIndent).join(self.fancyRepr(item, newIndent2) for item in obj))+u"\n"+indent+u"]"
        elif type(obj) == tuple:
            if len(obj) == 0:
                return u"()"
            return u"(\n"+newIndent+((u"\n"+newIndent).join(self.fancyRepr(item, newIndent2) for item in obj))+u"\n"+indent+u")"
        elif hasattr(obj, "__class__") and obj.__class__ == Cookie:
            return self.fancyRepr(obj.value)
        elif hasattr(obj, "__class__") and obj.__class__ == HeaderDict:
            return self.fancyRepr(obj.headers)
        elif hasattr(obj, "__unicode__") or type(obj) == unicode:
            return u"""[{1}] u"{0}\"""".format(unicode(obj), type(obj))
        elif hasattr(obj, "__str__") or type(obj) == str:
            return u"""[{1}] "{0}\"""".format(str(obj).decode("ascii", "backslashreplace"), type(obj))
        elif obj is None:
            return u"None"
        else:
            return u"[{1}] {0}".format(repr(obj), type(obj))
        
    def generatePlainTextMessage(self, trans, exceptionType, exception, tb):
        result = u"".join(traceback.format_exception(exceptionType, exception, tb))
        result += u"""

Query parameters:
GET: 
{0}

POST:
{1}

Cookies:
{2}

Headers:
{3}""".format(
            self.fancyRepr(trans.get_fields_from_path("utf-8")) if not trans.hide_get else u"Hidden intentionally",
            (self.fancyRepr(trans.post_query) if hasattr(trans, "post_query") else self.fancyRepr(trans.get_fields_from_body("utf-8"))) if not trans.hide_post else u"Hidden intentionally",
            self.fancyRepr(trans.get_cookies()) if not trans.hide_cookies else u"Hidden intentionally",
            self.fancyRepr(trans.get_headers()) if not trans.hide_headers else u"Hidden intentionally"
        )
        return result
        
    def handleException(self, trans, exceptionType, exception, tb):
        plainTextMessage = u"""On request: {0} {1}
the following exception occured at {2}:

""".format(trans.get_request_method(), trans.get_path(), TimeUtils.nowDate().isoformat())
        plainTextMessage += self.generatePlainTextMessage(trans, exceptionType, exception, tb)
        print(plainTextMessage.encode("utf-8"))
        
        if "mail-to" in errors:
            try:
                mailConfig = errors["mail-to"]
                subject = mailConfig["subject"].format(exceptionType.__name__, unicode(exception))
                to = mailConfig["to"]
                sender = mailConfig["sender"]
                smtp = mailConfig["smtp"]
                
                mail = MIMEText(plainTextMessage)
                mail["Subject"] = subject
                mail["To"] = ",".join(to)
                mail["From"] = sender
                mail["Date"] = self.model.formatHTTPTimestamp(TimeUtils.now())
                
                host = smtp["host"]
                port = int(smtp.get("port", 25))
                user = smtp.get("user", None)
                password = smtp.get("password", None)
                secure = smtp.get("secure", None)
                if not secure in ["starttls", "ssl"]:
                    raise ValueError("Invalid value for secure: {0}".format(secure))
                if secure == "ssl":
                    conn = smtplib.SMTP_SSL(host, port)
                else:
                    conn = smtplib.SMTP(host, port)
                    if secure == "starttls":
                        conn.starttls()
                if user is not None and password is not None:
                    conn.login(user, password)
                conn.sendmail(mail["From"], mail["To"], mail.as_string())
                conn.quit()
            except Exception as e :
                print("Could not send exception mail: {0}".format(e))
        
        trans.rollback()
        trans.set_response_code(500)
        self.out = trans.get_response_stream()
        trans.set_content_type(ContentType("text/html", "utf-8"))

        s = u"""
<html>
    <head>
        <title>Priyom.org internal API error</title>
        <link rel="stylesheet" type="text/css" href="{0}"/>
    </head>
    <body>
        <h1>Internal API error</h1>""".format(application.get("urlroot", u"") + u"/css/error.css")
        if self.show:
            s += u"""
        <h2>Error information</h2>
        <dl class="exc-info">
            <dt>Exception class:</dt>
            <dd>{1}</dd>
            <dt>Message:</dt>
            <dd>{2}</dd>
        </dl>
        <h2>Stacktrace</h2>
        <p>(most recent call last)</p>
        <ul>{0}</ul>""".format(
                u"\n".join((u"""<li><div class="tb-item-head">File &quot;<span class="tb-file">{0}</span>&quot;, line <span class="tb-lineno">{1:d}</span>, in <span class="tb-func">{2}</span></div><div class="tb-item-code">{3}</div>""".format(escape(os.path.relpath(filename, application["root"])), lineno, escape(funcname), escape(text)) for (filename, lineno, funcname, text) in traceback.extract_tb(tb))), 
                
                escape(unicode(exceptionType)),
                escape(unicode(exception)).replace("\n", "<br/>")
            )
                
        else:
            s += u"""
        <p>An internal error has occured. Please report this to <a href="mailto:{0}">{1}</a></p>""".format(admin["mail"], admin["name"])
            
        s += u"""
    </body>
</html>"""
        print >>self.out, s.encode("utf-8")

    
    def respond(self, trans):
        trans.hide_post = False
        trans.hide_get = False
        trans.hide_cookies = False
        trans.hide_headers = False
        try:
            self.resource.respond(trans)
        except EndOfResponse:
            raise
        except:
            eType, e, tb = sys.exc_info()
            self.handleException(trans, eType, e, tb)
            
            # first make a print to stdout, this will give us a log in 
            # the apache:
            
                
