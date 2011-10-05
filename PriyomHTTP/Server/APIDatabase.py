"""
File name: APIDatabase.py
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
from storm.locals import *
import random
from hashlib import sha256
import time
from datetime import datetime
from libPriyom.Formatting import priyomdate
import netaddr
from libPriyom.Helpers import TimeUtils
from cfg_priyomhttpd import application
import os.path

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
    CIDRList = Unicode()
    
    def checkCIDR(self, srcIP):
        if self.CIDRList is None:
            return True
        if srcIP is None:
            return False
        try:
            srcIP = netaddr.IPAddress(srcIP)
        except:
            return False
        try:
            cidrs = [netaddr.IPNetwork(item.rstrip().lstrip()) for item in self.CIDRList.split(",")]
            return netaddr.smallest_matching_cidr(srcIP, cidrs) is not None
        except:
            return True
    
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
        sid = unicode(sha256(unicode(int(TimeUtils.now()))).hexdigest())
        while store.find(APISession, APISession.Key == sid).any() is not None:
            sid = unicode(sha256(unicode(int(TimeUtils.now()))+unicode(rnd.randint(0, 655535))).hexdigest())
        
        # create a new session
        session = APISession(sid, self.ID, int(TimeUtils.now() + 86400))
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
        return (store is not None) and (len(self.Key) > 0) and (self.Expires > TimeUtils.now())
        
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
    
class APINews(object):
    __storm_table__ = "api-news"
    
    ID = Int(primary=True)
    Title = Unicode()
    Contents = Unicode()
    Timestamp = Int()
    
    def html_row(self):
        return u"""<tr><td>%s</td><th>%s</th><td><p>%s</p></td></tr>""" % (datetime.fromtimestamp(self.Timestamp).strftime(priyomdate), self.Title, self.Contents)
        
class APIFileResource(object):
    __storm_table__ = "api-fileResources"
    
    ID = Int(primary=True)
    ReferenceTable = Unicode()
    LocalID = Int()
    ResourceType = Unicode()
    Timestamp = Int()
    FileName = Unicode()
    
    def __init__(self, refTable, id, resourceType, timestamp, fileFormat):
        self.ReferenceTable = refTable
        self.LocalID = id
        self.ResourceType = resourceType
        self.Timestamp = timestamp
        
        hash = sha256(refTable)
        hash.update(unicode(id))
        hash.update(resourceType)
        hash.update(unicode(timestamp))
        digest = hash.hexdigest()
        
        self.FileName = fileFormat.format(application["root"], digest)
    
    @staticmethod
    def createOrFind(store, refTable, id, resourceType, timestamp, fileFormat, createCallback):
        store.execute("LOCK TABLES `api-fileResources` READ")
        try:
            item = store.find(
                APIFileResource,
                APIFileResource.ReferenceTable == refTable,
                APIFileResource.LocalID == id,
                APIFileResource.ResourceType == resourceType,
                APIFileResource.Timestamp == timestamp
            ).any()
            if item is None:
                store.execute("LOCK TABLES `api-fileResources` WRITE")
                item = store.find(
                    APIFileResource,
                    APIFileResource.ReferenceTable == refTable,
                    APIFileResource.LocalID == id,
                    APIFileResource.ResourceType == resourceType,
                    APIFileResource.Timestamp == timestamp
                ).any()
                if item is None:
                    for resource in store.find(
                                        APIFileResource, 
                                        APIFileResource.ReferenceTable == refTable,
                                        APIFileResource.LocalID == id,
                                        APIFileResource.ResourceType == resourceType
                                    ):
                        os.unlink(resource.FileName)
                    item = APIFileResource(refTable, id, resourceType, timestamp, fileFormat)
                    store.add(item)
                    store.execute("UNLOCK TABLES")
                    store.flush()
                    try:
                        createCallback(item)
                    except:
                        store.execute("LOCK TABLES `api-fileResources` WRITE")
                        store.remove(item)
                        store.execute("UNLOCK TABLES")
                        raise
        finally:
            store.execute("UNLOCK TABLES")
        if not os.path.isfile(item.FileName):
            store.execute("LOCK TABLES `api-fileResources` WRITE")
            store.remove(item)
            store.execute("UNLOCK TABLES")
            return APIFileResource.createOrFind(store, refTable, id, resourceType, timestamp, fileFormat, createCallback)
        return item
    
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
