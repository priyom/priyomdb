#!/usr/bin/python2.7
"""
File name: admin.py
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
from libPriyom import *
from PriyomHTTP.Server.APIDatabase import *
from cfg_priyomhttpd import database

db = create_database(database["stormURL"])
store = Store(db)
intf = PriyomInterface(store)

def addUser(userName, eMail, password):
    userName = userName if type(userName) == unicode else unicode(userName, "UTF-8")
    eMail = eMail if type(eMail) == unicode else unicode(eMail, "UTF-8")
    password = password if type(password) == unicode else unicode(password, "UTF-8")
    if store.find(APIUser, Or(APIUser.UserName == userName, APIUser.EMail == eMail)).any() is not None:
        return "Is not unique."
    user = APIUser()
    user.UserName = userName
    user.EMail = eMail
    user.setPassword(password)
    store.add(user)
    store.flush()
    return "User created: %d" % (user.ID)
    
def addCapability(capabilityName):
    capabilityName = capabilityName if type(capabilityName) == unicode else unicode(capabilityName, "UTF-8")
    cap = store.find(APICapability, APICapability.Capability == capabilityName).any()
    if cap is not None:
        raise Exception('Capability exists: %s' %(capabilityName))
    cap = APICapability()
    cap.Capability = capabilityName
    store.add(cap)
    store.flush()
    return "Capability created: %d" % (cap.ID)

def assignCapability(userName, capabilityName):
    userName = userName if type(userName) == unicode else unicode(userName, "UTF-8")
    capabilityName = capabilityName if type(capabilityName) == unicode else unicode(capabilityName, "UTF-8")
    user = store.find(APIUser, APIUser.UserName == userName).any()
    if user is None:
        raise Exception('User not found: %s' % (userName))
    cap = store.find(APICapability, APICapability.Capability == capabilityName).any()
    if cap is None:
        raise Exception('Capability not found: %s' %(capabilityName))
    user.Capabilities.add(cap)
    store.flush()
    return "Capability assigned"

def addNews(title, contents):
    news = APINews()
    store.add(news)
    try:
        news.Title = title
        news.Contents = contents
    except:
        store.remove(news)
        return
    news.Timestamp = int(TimeUtils.now())
    store.flush()
    return "News added #%d" % news.ID
