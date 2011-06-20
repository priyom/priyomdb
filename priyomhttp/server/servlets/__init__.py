import storm.exceptions
import os
import os.path
known_servlets = {}
loaded_servlets = {}
priyomInterface = None

class DuplicateServletError(Exception):
    pass
    

def get(servletName):
    global known_servlets, loaded_servlets, priyomInterface
    if priyomInterface is None:
        raise libpriyom.interface.NoPriyomInterfaceError()
    if servletName in loaded_servlets:
        return loaded_servlets[servletName]
    elif servletName in known_servlets:
        servlet = known_servlets[servletName](servletName, priyomInterface)
        loaded_servlets[servletName] = servlet
        return servlet
    else:
        return None

def register(servletName, servletClass, allowReplace=True, fileName=None):
    global known_servlets
    if not allowReplace and servletName in known_servlets:
        raise DuplicateServletError("Servlet \"%s\" already registered." % servletName)
    known_servlets[servletName] = servletClass
    # print(u"%s/%s/%s" % (os.getcwdu(), os.path.join(*__package__.split(u".")), fileName))
    # ToDo: Implement watching here for transparent exchange of servlets

import station
import stations
import broadcasts
