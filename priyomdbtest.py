#!/usr/bin/python2.7
from storm.locals import *
from libPriyom import *
from libPriyom.Helpers.ScheduleMaintainer import ScheduleMaintainer
import xml.dom.minidom as dom
from cfg_priyomhttpd import userpass, database

db = create_database("mysql://%s@localhost/%s" % (userpass, database))
store = Store(db)
store.autoreload()
buzzer = store.get(Station, 1)
test = store.get(Station, 2)
intf = PriyomInterface(store)

doc = dom.getDOMImplementation().createDocument(XMLIntf.namespace, "priyom-db-export", None)
#intf.exportStationToDom(buzzer, None, doc)
#print(doc.toprettyxml())
sched = intf.scheduleMaintainer
start = ScheduleMaintainer.now()
#sched.updateSchedule(test, start+86400*7)
#store.flush()
