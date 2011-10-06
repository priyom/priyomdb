"""
File name: Plot.py
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
from WebStack.Generic import ContentType, EndOfResponse
from libPriyom import *
from API import API, CallSyntax, Argument
from ...APIDatabase import APIFileResource
import mmap
from cfg_priyomhttpd import application
from libPriyom.PlotDataSources import NoDataError, NoDataArgError

class PlotAPI(API):
    def __init__(self, model, dataSource, renderer, queryArgs, resourceType, fileFormat=u"{0}/{{1}}.png", contentType=ContentType("image/png"), **kwargs):
        super(API, self).__init__(model)
        self.dataSource = dataSource
        self.renderer = renderer
        self.plotArgs = kwargs
        self.allowedMethods = frozenset(['GET'])
        self.queryArgs = queryArgs
        self.resourceType = resourceType
        self.fileFormat = fileFormat.format(application["plots"])
        self.contentType = contentType
        
    def plot(self, resource, tmpArgs):
        self.renderer.plotGraph(self.dataSource, resource.FileName, dpi=72, format="png", transparent=True, **tmpArgs)
        
    def handle(self, trans):
        args = {}
        for tuple in self.queryArgs:
            queryName, typecast, kwName = tuple[:3]
            try:
                if not queryName in self.query:
                    if len(tuple) == 4:
                        args[kwName] = tuple[3]
                    else:
                        self.parameterError(queryName, u"must be {0}".format(typecast))
                else:
                    args[kwName] = self.query[queryName] if typecast is None else typecast(self.query[queryName])
            except TypeError as e:
                self.parameterError(queryName, unicode(e))
            except ValueError as e:
                self.parameterError(queryName, unicode(e))
        tmpArgs = self.plotArgs.copy()
        tmpArgs.update(args)
        lastModified = self.dataSource.getLastModified(**tmpArgs)
        
        try:
            if lastModified is None:
                raise NoDataArgError(tmpArgs)
            
            trans.set_content_type(self.contentType)
            trans.set_header_value("Last-Modified", self.model.formatHTTPTimestamp(lastModified))
            self.autoNotModified(lastModified)
        
            item = APIFileResource.createOrFind(self.store, self.resourceType, tmpArgs, lastModified, self.fileFormat, self.plot)
        except NoDataError as e:
            trans.set_response_code(404)
            trans.set_content_type(ContentType("text/plain", self.encoding))
            print >>self.out, unicode(e).encode(self.encoding)
            raise EndOfResponse
            
        if item is not None:
            img = open(item.FileName, "rb")
            map = mmap.mmap(img.fileno(), 0, flags=mmap.MAP_SHARED, prot=mmap.PROT_READ)
            trans.disableCompression()
            print >>self.out, map.read(map.size())
            map.close()
            img.close()
        else:
            raise Exception(u"Could not create resource.")
        
