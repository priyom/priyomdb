from storm.locals import *
import random
from hashlib import sha256
import time
from datetime import datetime

def now():
    return int(time.mktime(datetime.utcnow().timetuple()))

rnd = random.SystemRandom()

class APICapableObject(object):
    def __contains__(self, capability):
        return capability in (cap.Capability for cap in self.Capabilities)
    
    def getCaps(self):
        return [cap.Capability for cap in self.Capabilities]

class APIKey(APICapableObject):
    __storm_table__ = "api-keys"
    
    ID = Int(primary=True)
    Key = Unicode()
    
class APIUser(APICapableObject):
    __storm_table__ = "api-users"
    
    ID = Int(primary=True)
    UserName = Unicode()
    EMail = Unicode()
    PasswordHash = Unicode()
    PasswordSalt = Unicode()
    
    def __init__(self):
        self.PasswordSalt = u"".join((hex(rnd.randint(0, 65535))[2:] for i in xrange(0, 5)))
    
    def getSession(self):
        store = Store.of(self)
        if store is None:
            return None
        if len(self.UserName) == 0 or len(self.EMail) == 0 or len(self.PasswordHash) == 0:
            return None
        # delete old sessions
        old = store.find(APISession, APISession.UserID == self.ID).any()
        if old is not None:
            old.delete()
        
        # generate a new session id
        sid = unicode(sha256(unicode(now())).hexdigest())
        while store.find(APISession, APISession.Key == sid).any() is not None:
            sid = unicode(sha256(unicode(now())+unicode(rnd.randint(0, 655535))).hexdigest())
        
        # create a new session
        session = APISession(sid, self.ID, now() + 86400)
        store.add(session)
        for cap in self.Capabilities:
            session.Capabilities.add(cap)
        return session
        
    def checkPassword(self, password):
        return sha256(password + self.PasswordSalt).hexdigest() == self.PasswordHash
        
    def setPassword(self, password):
        self.PasswordHash = unicode(sha256(password + self.PasswordSalt).hexdigest(), "UTF-8")

class APISession(APICapableObject):
    __storm_table__ = "api-sessions"
    
    ID = Int(primary = True)
    Key = Unicode()
    UserID = Int()
    Expires = Int()
    
    def __init__(self, key, userId, expires):
        self.Key = key
        self.UserID = userId
        self.Expires = expires
        
    def isValid(self):
        store = Store.of(self)
        return (store is not None) and (len(self.Key) > 0) and (self.Expires > now())
        
    def delete(self):
        store = Store.of(self)
        store.find(APISessionCapability, APISessionCapability.SessionID == self.ID).remove()
        store.remove(self)
        
    
class APICapability(object):
    __storm_table__ = "api-capabilities"
    
    ID = Int(primary=True)
    Capability = Unicode()
    
class APIKeyCapability(object):
    __storm_table__ = "api-keyCapabilities"
    __storm_primary__ = "KeyID", "CapabilityID"
    
    KeyID = Int()
    CapabilityID = Int()
    
class APIUserCapability(object):
    __storm_table__ = "api-userCapabilities"
    __storm_primary__ = "UserID", "CapabilityID"
    
    UserID = Int()
    CapabilityID = Int()
    
class APISessionCapability(object):
    __storm_table__ = "api-sessionCapabilities"
    __storm_primary__ = "SessionID", "CapabilityID"
    
    SessionID = Int()
    CapabilityID = Int()
    
class Variable(object):
    __storm_table__ = "variables"
    
    Name = Unicode(primary=True)
    Value = Unicode()
    
APIKey.Capabilities = ReferenceSet(
    APIKey.ID, 
    APIKeyCapability.KeyID,
    APIKeyCapability.CapabilityID,
    APICapability.ID)
APIUser.Capabilities = ReferenceSet(
    APIUser.ID,
    APIUserCapability.UserID,
    APIUserCapability.CapabilityID,
    APICapability.ID)
APISession.Capabilities = ReferenceSet(
    APISession.ID,
    APISessionCapability.SessionID,
    APISessionCapability.CapabilityID,
    APICapability.ID)
