"""
File name: api.py
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
import sys
sys.path.append('/etc/priyomdb/')
from cfg_priyomhttpd import application, database
sys.path.append(application["root"])



from WebStack.Adapters.WSGI import WSGIAdapter
from PriyomHTTP.Server.WebStackResource import get_site_map
from libPriyom.Interface import PriyomInterface
from libPriyom.Structure import libPriyomSchema
from storm.locals import *

db = create_database(database["stormURL"])
store = Store(db)
libPriyomSchema.upgrade(store)
intf = PriyomInterface(store)

application = WSGIAdapter(get_site_map(intf), handle_errors=0)
