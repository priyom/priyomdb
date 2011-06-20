#!/usr/bin/python2.7
from storm.locals import *
import priyomhttp.server
import BaseHTTPServer
import libpriyom.interface
import priyomhttp.server.servlets

db = create_database("mysql://priyom-test:priyom-test@localhost/priyom-test")
store = Store(db)
iface = libpriyom.interface.PriyomInterface(store)
priyomhttp.server.servlets.priyomInterface = iface

server = BaseHTTPServer.HTTPServer(("", 8080), priyomhttp.server.PriyomHTTPRequestHandler, True)
server.serve_forever()
