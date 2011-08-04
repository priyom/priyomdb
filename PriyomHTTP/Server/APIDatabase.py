from storm.locals import *

class APIKey(object):
    __storm_table__ = "api-keys"
    
    ID = Int(primary=True)
    Key = Unicode()
    
    def getCaps():
        return [cap.Capability for cap in self.Capabilities]
    
class APICapability(object):
    __storm_table__ = "api-capabilities"
    
    ID = Int(primary=True)
    Capability = Unicode()
    
class APIKeyCapability(object):
    __storm_table__ = "api-keyCapabilities"
    __storm_primary__ = "KeyID", "CapabilityID"
    
    KeyID = Int()
    CapabilityID = Int()
    
APIKey.Capabilities = ReferenceSet(
    APIKey.ID, 
    APIKeyCapability.KeyID,
    APIKeyCapability.CapabilityID,
    APICapability.ID)
