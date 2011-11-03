#!/usr/bin/python2
"""
File name: clearPlotCache.py
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
