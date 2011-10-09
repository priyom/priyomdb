# encoding=utf-8
"""
File name: SubmitResource.py
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
from storm.locals import *
from HTMLResource import HTMLResource
from libPriyom import *
from datetime import datetime, timedelta
from time import mktime, time
import itertools
import xml.etree.ElementTree as ElementTree


class SubmitParameterError(BaseException):
    pass



class SubmitResource(HTMLResource):
    def _stationSelect(self, parent, name=u"station", value=None):
        stationSelect = self.SubElement(parent, u"select", name=name)
        for station in self.store.find(Station).order_by(Asc(Station.EnigmaIdentifier), Asc(Station.PriyomIdentifier), Asc(Station.Nickname)):
            stationOption = self.SubElement(stationSelect, u"option", value=unicode(station.ID))
            if station == value:
                stationOption.set(u"selected", u"selected")
            stationOption.text = unicode(station)

        
    def _modulationSelector(self, name=u"modulation", value=u""):
        if self.modulationSelector is None:
            self.modulationSelector = ElementTree.Element(u"{{{0}}}select".format(XMLIntf.xhtmlNamespace))
            for modulation in self.store.find(Modulation).order_by(Asc(Modulation.Name)):
                option = self.SubElement(self.modulationSelector, u"option", value=modulation.Name)
                option.text = modulation.Name
        
        select = self.modulationSelector.copy()
        for option in select:
            if option.text == value:
                option.set(u"selected", u"selected")
                break
        select.set(u"name", name)
        return select
    
    @staticmethod
    def recursiveDictNode(dictionary, indent = u""):
        for key, value in dictionary.iteritems():
            if type(value) == dict:
                yield u"""{1}{0}: {2}""".format(key, indent, u"{")
                for line in SubmitResource.recursiveDictNode(value, indent + u"    "):
                    yield line
                yield u"""{0}{1}""".format(indent, u"}")
            else:
                yield u"""{2}{0}: {1}""".format(key, repr(value), indent)
    
    @staticmethod
    def recursiveDict(dict):
        return "\n".join(SubmitResource.recursiveDictNode(dict))
        
    def section(self, parent, title):
        sec = self.SubElement(parent, u"div", attrib={
            u"class": u"section"
        })
        self.SubElement(sec, u"div", attrib={
            u"class": u"inner-caption"
        }).text = title
        return sec
        
    def buildDoc(self, trans, elements):
        self.error = None
        self.modulationSelector = None
        
    def setError(self, message):
        if self.error is not None:
            raise SubmitParameterError()
        self.error = message
        raise SubmitParameterError()
        
    def parameterError(self, parameterName, message=None):
        self.error = u"{0} is wrong: {1}".format(parameterName, message)
