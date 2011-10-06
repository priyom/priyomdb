#!/usr/bin/python2.7
"""
File name: priyomdbtest.py
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
from libPriyom.Helpers.ScheduleMaintainer import ScheduleMaintainer
import xml.dom.minidom as dom
from cfg_priyomhttpd import database
from libPriyom.Plots import *
from libPriyom.PlotDataSources import *

db = create_database(database["stormURL"])
store = Store(db)
buzzer = store.get(Station, 1)
test = store.get(Station, 2)
intf = PriyomInterface(store)

doc = dom.getDOMImplementation().createDocument(XMLIntf.namespace, "priyom-db-export", None)
#intf.exportStationToDom(buzzer, None, doc)
#print(doc.toprettyxml())
sched = intf.scheduleMaintainer
