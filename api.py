from WebStack.Adapters.ModPython import deploy
from PriyomHTTP.Server.WebStackResource import get_site_map
from libPriyom.Interface import PriyomInterface
from storm.locals import *
from cfg_priyomhttpd import userpass, database

db = create_database("mysql://%s@localhost/%s" % (userpass, database))
store = Store(db)
store.autoreload() # not a good solution, but that'll do the trick
intf = PriyomInterface(store)

handler, _no_authentication = deploy(get_site_map(intf), handle_errors=0)
