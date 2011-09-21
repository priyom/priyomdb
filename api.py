import sys
sys.path.append('/etc/priyomdb/')
from cfg_priyomhttpd import application, database
sys.path.append(application["root"])



from WebStack.Adapters.WSGI import WSGIAdapter
from PriyomHTTP.Server.WebStackResource import get_site_map
from libPriyom.Interface import PriyomInterface
from storm.locals import *

db = create_database(database["stormURL"])
store = Store(db)
intf = PriyomInterface(store)

application = WSGIAdapter(get_site_map(intf), handle_errors=0)
