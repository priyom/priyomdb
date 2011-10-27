# encoding=utf-8
"""
File name: CatchDisconnect.py
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
from WebStack.Generic import EndOfResponse, ContentType
from storm.exceptions import DisconnectionError
from _mysql_exceptions import ProgrammingError

class CatchDisconnectSelector(object):
    maxNesting = 10
    
    def __init__(self, resource, store):
        self.resource = resource
        self.store = store
        self.nesting = 0
        
    def catch(self, trans, error):
        self.store.rollback()
        trans.rollback()
        self.nesting += 1
        if self.nesting >= CatchDisconnectSelector.maxNesting:
            trans.rollback()
            trans.set_response_code(503)
            trans.set_content_type(ContentType("text/plain", "utf-8"))
            print >>trans.get_response_stream(), error.encode("utf-8")
        else:
            self.handle(trans)
        
    def respond(self, trans):
        self.nesting = 0
        return self.handle(trans)
        
    def handle(self, trans):
        try:
            return self.resource.respond(trans)
        except DisconnectionError:
            # In that case, we perform a reconnect, flush the cache,
            # write a message into the errorlog and try to re-execute the
            # resource.
            print("[{0}]: Attempting to reconnect after receiving a DisconnectionError".format(type(self).__name__))
            self.catch(trans, u"Every attempt to get a database connection working failed")
        except ProgrammingError as e:
            # This may be a commands out of sync. Lets check for that, 
            # otherwise we just pass this on
            if "commands out of sync" in str(e).lower():
                print("[{0}]: Caught a {1}".format(type(self).__name__, str(e)))
                self.catch(trans, u"Keeping to receive a commands out of sync from mysql.")
            else:
                raise
