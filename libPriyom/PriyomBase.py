# encoding=utf-8
from storm.locals import *
from storm.exceptions import NoStoreError
import time
from datetime import datetime
from Helpers.TimeUtils import now

def AutoSetModified(instance, propertyName, newValue):
    instance.touch()
    return newValue

class PriyomBase(object):
    Created = Int()
    Modified = Int()
    _knownModified = None
    
    def __init__(self):
        self.Created = int(now())
        self.Modified = int(now())
    
    def _forceStore(self, exceptionMessage = None):
        store = Store.of(self)
        if store is None:
            raise NoStoreError(exceptionMessage if exceptionMessage is not None else u"A store is needed to do that.")
        return store
    
    def invalidated(self):
        self._forceStore(u"A store is needed to determine the valid status of an object.")
        self.Modified = AutoReload
        if self._knownModified is None:
            self._knownModified = self.Modified
            return True
        if self._knownModified != self.Modified:
            return False
        
    def validate(self):
        store = self._forceStore(u"A store is needed to validate an object.")
        self.Modified = AutoReload
        if self._knownModified != self.Modified:
            store.autoreload(self)
            self._knownModified = self.Modified
            
    def touch(self, newModified = None):
        if newModified is None:
            self.Modified = int(now())
        else:
            self.Modified = newModified
