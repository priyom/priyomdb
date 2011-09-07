# encoding=utf-8
from storm.locals import *
from storm.exceptions import NoStoreError

class PriyomBase(object):
    Created = Int()
    Modified = Int()
    _knownModified = None
    
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
