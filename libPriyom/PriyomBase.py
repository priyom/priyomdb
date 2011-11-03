# encoding=utf-8
"""
File name: PriyomBase.py
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
