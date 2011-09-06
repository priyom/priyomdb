import sys
sys.path.append('/etc/priyomdb/')
from cfg_priyomhttpd import userpass, database, approot
sys.path.append(approot)



from WebStack.Adapters.WSGI import WSGIAdapter
from PriyomHTTP.Server.WebStackResource import get_site_map
from libPriyom.Interface import PriyomInterface
from storm.locals import *

db = create_database("mysql://%s@localhost/%s" % (userpass, database))
store = Store(db)
intf = PriyomInterface(store)

application = WSGIAdapter(get_site_map(intf))
