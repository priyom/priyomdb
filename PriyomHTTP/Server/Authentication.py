from WebStack.Generic import ContentType, EndOfResponse
from APIDatabase import APIKey

class AuthenticationSelector(object):
    def __init__(self, store, resource, requiredCapability):
        self.store = store
        self.resource = resource
        self.requiredCapability = requiredCapability
        
    def getAPIKey(self, keyList):
        if len(keyList) != 1:
            return None
        key = keyList[0]
        if type(key) != unicode:
            key = unicode(key, "UTF-8")
        return self.store.find(APIKey, APIKey.Key == unicode(key)).any()
        
    def continueWithAPIKey(self, trans, key):
        if self.requiredCapability in key.Capabilities:
            return self.resource.respond(trans)
        else:
            self.authFailed(trans)
            
    def authFailed(self, trans):
        trans.set_response_code(401)
        raise EndOfResponse
        
    def respond(self, trans):
        self.out = trans.get_response_stream()
        query = trans.get_fields_from_path()
        apiKey = None
        if "apikey" in query:
            apiKey = self.getAPIKey(query["apikey"])
        if apiKey is not None:
            return self.continueWithAPIKey(trans, apiKey)
        apiKey = self.getAPIKey(trans.get_header_values("X-API-Key"))
        if apiKey is not None:
            return self.continueWithAPIKey(trans, apiKey)
        self.authFailed(trans)
