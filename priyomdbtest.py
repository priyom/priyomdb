#!/usr/bin/python2.7
from storm.locals import *
from libpriyom import *
from libpriyom.helpers.scheduleMaintainer import ScheduleMaintainer
import xml.dom.minidom as dom

db = create_database("mysql://priyom-test:priyom-test@localhost/priyom-test")
store = Store(db)
buzzer = store.get(Station, 1)
test = store.get(Station, 2)
intf = PriyomInterface(store)

doc = dom.getDOMImplementation().createDocument(xmlintf.namespace, "priyom-db-export", None)
sched = intf.scheduleMaintainer
start = ScheduleMaintainer.now()
sched.updateSchedule(test, start+86400*7)
store.flush()
