from WebStack.Adapters.WSGI import deploy_with_wsgiref
from PriyomHTTP.Server.WebStackResource import get_site_map
from libPriyom.Interface import PriyomInterface
from storm.locals import *
from cfg_priyomhttpd import userpass, database

db = create_database("mysql://%s@localhost/%s" % (userpass, database))
store = Store(db)
intf = PriyomInterface(store)

handler = deploy_with_wsgiref(get_site_map(intf), handle_errors=0)
