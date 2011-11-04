"""
File name: Authentication.py
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
from PriyomHTTP.Server.APIDatabase import APIKey, APISession

class AuthenticationFailed(Exception):
    pass

class AuthenticationSelector(object):
    def __init__(self, store, resource):
        self.store = store
        self.resource = resource
        
    def getAPIKey(self, keyList):
        if len(keyList) != 1:
            return None
        key = keyList[0]
        if type(key) != unicode:
            key = unicode(key, "UTF-8")
        key = self.store.find(APIKey, APIKey.Key == unicode(key)).any()
        if key is None:
            return None
        if not key.checkCIDR(self.trans.env["REMOTE_ADDR"] if "REMOTE_ADDR" in self.trans.env else None):
            raise AuthenticationFailed("Forbidden use of an api key.")
        return key
        
    def getAPISession(self, idList):
        if len(idList) != 1:
            return None
        id = idList[0]
        if type(id) != unicode:
            id = unicode(id, "UTF-8")
        session = self.store.find(APISession, APISession.Key == unicode(id)).any()
        if session is None:
            return None
        elif not session.isValid():
            session.delete()
            raise AuthenticationFailed("Session timed out.")
        else:
            return session
        
    def continueWithAPICapable(self, trans, capObj):
        trans.apiAuth = True
        trans.apiCaps = capObj.getCaps()
        return self.resource.respond(trans)
        
    def respond(self, trans):
        trans.apiAuthError = None
        self.trans = trans
        self.out = trans.get_response_stream()
        query = trans.get_fields_from_path()
        try:
            apiKey = None
            if "apikey" in query:
                apiKey = self.getAPIKey(query["apikey"])
            if apiKey is not None:
                return self.continueWithAPICapable(trans, apiKey)
            apiKey = self.getAPIKey(trans.get_header_values("X-API-Key"))
            if apiKey is not None:
                return self.continueWithAPICapable(trans, apiKey)
                
            apiSession = None
            if "sid" in query:
                apiSession = self.getAPISession(query["sid"])
            if apiSession is None:
                apiSession = self.getAPISession(trans.get_header_values("X-API-Session"))
            if apiSession is None:
                cookie = trans.get_cookie("priyom-api-session")
                if cookie is not None:
                    apiSession = self.getAPISession([cookie.value])
            
            if apiSession is not None:
                return self.continueWithAPICapable(trans, apiSession)
        except AuthenticationFailed as e:
            trans.apiAuthError = e.message
        trans.apiAuth = False
        trans.apiCaps = []
        return self.resource.respond(trans)
