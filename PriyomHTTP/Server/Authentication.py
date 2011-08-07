from WebStack.Generic import ContentType, EndOfResponse
from APIDatabase import APIKey, APISession

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
        return self.store.find(APIKey, APIKey.Key == unicode(key)).any()
        
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
            return None
        else:
            return session
        
    def continueWithAPICapable(self, trans, capObj):
        trans.apiAuth = True
        trans.apiCaps = capObj.getCaps()
        return self.resource.respond(trans)
        
    def respond(self, trans):
        self.out = trans.get_response_stream()
        query = trans.get_fields_from_path()
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
        if apiSession is not None:
            return self.continueWithAPICapable(trans, apiSession)
        apiSession = self.getAPISession(trans.get_header_values("X-API-Session"))
        if apiSession is not None:
            return self.continueWithAPICapable(trans, apiSession)
        
        trans.apiAuth = False
        trans.apiCaps = []
        return self.resource.respond(trans)
