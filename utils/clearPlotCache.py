#!/usr/bin/python2
import sys
sys.path.append('/etc/priyomdb/')
from cfg_priyomhttpd import application
sys.path.append(application["root"])
from priyomdbtest import *
from PriyomHTTP.Server.APIDatabase import APIFileResource
import os
import os.path
store.execute("LOCK TABLES `api-fileResources` WRITE")
resources = store.find(APIFileResource)
for resource in list(resources):
  if os.path.isfile(resource.FileName):
    try:
      os.unlink(resource.FileName)
      store.remove(resource)
    except OSError as e:
      print(unicode(e))
      pass
store.execute("UNLOCK TABLES")