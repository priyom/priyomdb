#!/usr/bin/python2.7
from storm.locals import *
from libPriyom import *
from PriyomHTTP.Server.APIDatabase import *
from cfg_priyomhttpd import userpass, database

db = create_database("mysql://%s@localhost/%s" % (userpass, database))
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
