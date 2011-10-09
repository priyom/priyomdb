# encoding=utf-8
"""
File name: SubmitLog.py
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
from storm.expr import *
from WebStack.Generic import ContentType, EndOfResponse
from SubmitResource import SubmitResource, SubmitParameterError
from libPriyom import *
from datetime import datetime, timedelta
from time import mktime, time
import itertools
import xml.etree.ElementTree as ElementTree
import math

class SubmitLogResource(SubmitResource):
    def __init__(self, model):
        super(SubmitLogResource, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
        
        
        self.stationValidator = self.model.validStormObject(Station, self.store)
        self.timestampValidator = self.model.PriyomTimestamp()
        self.durationValidator = float
        self.unicodeValidator = unicode
        
        self.broadcastValidator = self.model.AllowBoth(self.model.validStormObject(Broadcast, self.store), self.model.EmptyString())
        
        self.transmissionClassValidator = self.model.validStormObject(TransmissionClass, self.store)


    def _basicInformationTree(self, parent):
        parent[0].tail = u"Station: "
        stationSelect = self._stationSelect(parent, name=u"station", value=self.station)
        
        self.br(parent, u"Timestamp: ")
        self.input(parent, name=u"timestamp", value=unicode(self.timestamp.strftime(Formatting.priyomdate)))
        
        self.br(parent, u"Duration: ")
        self.input(parent, name=u"duration", value=unicode(self.duration)).tail = u" s"
        
        self.br(parent, u"Callsign: ")
        self.input(parent, name=u"callsign", value=self.callsign)
        
        self.br(parent, u"Foreign callsign (langCode / contents): ")
        self.input(parent, name=u"foreignCallsign[lang]", value=self.foreignCallsignLang).tail = u" / "
        self.input(parent, name=u"foreignCallsign[value]", value=self.foreignCallsign)
        
        self.br(parent, u"Remarks: ")
        self.input(parent, name=u"remarks", value=self.remarks)
        
        self.br(parent, u"Recording URL: ")
        self.input(parent, name=u"recording", value=self.recordingURL)
        
    def _frequencyTable(self, parent):
        table = self.SubElement(parent, u"table", attrib={
            u"class": u"frequency-table"
        })
        head = self.SubElement(table, u"thead")
        self.SubElement(head, u"th").text = u"Frequency"
        self.SubElement(head, u"th").text = u"Modulation/Mode"
        self.SubElement(head, u"th").set(u"class", u"buttons")
        
        body = self.SubElement(table, u"tbody")
        
        freqs = list(itertools.ifilter((lambda kv: (kv[0] != "new" or "submit" in kv[1]) and (not "delete" in kv[1])), self.queryEx.get("frequencies", {}).iteritems()))
        freqs.sort(key=lambda x: x[0])
        for i, (key, item) in itertools.izip(xrange(len(freqs)), freqs):
            if "submit" in item:
                part = item["frequency+modulation"].partition(u" ")
                item["frequency"] = part[0]+u" Hz"
                item["modulation"] = part[2]
            freq = BroadcastFrequency.parseFrequency(item["frequency"])
            if freq is None:
                freq = "0 Hz"
            else:
                freq = BroadcastFrequency.formatFrequency(freq)
            
            tr = self.SubElement(body, u"tr")
            self.input(self.SubElement(tr, u"td"), name=u"frequencies[{0}][frequency]".format(i), value=freq)
            self.SubElement(tr, u"td").append(self._modulationSelector(name=u"frequencies[{0}][modulation]".format(i), value=item["modulation"]))
            buttons = self.SubElement(tr, u"td", attrib={
                u"class": u"buttons"
            })
            self.input(buttons, type=u"submit", name=u"frequencies[{0}][update]".format(i), value=u"Save")
            self.input(buttons, type=u"submit", name=u"frequencies[{0}][delete]".format(i), value=u"✗")
        
        knownFrequencies = self.store.using(
            BroadcastFrequency, 
            LeftJoin(Modulation, Modulation.ID == BroadcastFrequency.ModulationID), 
            LeftJoin(Broadcast, BroadcastFrequency.BroadcastID == Broadcast.ID)
        ).find(
            (BroadcastFrequency.Frequency, Modulation.Name), 
            Broadcast.StationID == self.station.ID
        ).config(distinct=True) if self.station is not None else None
        
        tr = self.SubElement(body, u"tr")
        td = self.SubElement(body, u"td", attrib={
            u"class": u"buttons",
            u"colspan": u"3"
        })
        self.input(td, type=u"submit", name=u"frequencies[new][submit]", value=u"+")
        select = self.SubElement(td, u"select", name=u"frequencies[new][frequency+modulation]")
        option = self.SubElement(select, u"option", value=u"0 USB").text=u"0 Hz (USB)"
        if knownFrequencies is not None:
            for frequency, modulation in knownFrequencies:
                self.SubElement(select, u"option", value=u"{0} {1}".format(frequency, modulation)).text = u"{0} ({1})".format(BroadcastFrequency.formatFrequency(frequency), modulation)
        
        return table
        
        
    def _broadcastTree(self, parent):
        broadcastSelect = self.SubElement(parent, u"select", name=u"broadcast")
        self.SubElement(broadcastSelect, u"option", value=u"").text = u"New broadcast"
        found = False
        if self.station is not None and self.timestamp is not None:
            for broadcast in self.priyomInterface.getCloseBroadcasts(self.station.ID, TimeUtils.toTimestamp(self.timestamp), 600)[1]:
                if broadcast.type == u"continous":
                    continue
                broadcastOption = self.SubElement(broadcastSelect, u"option", value=unicode(broadcast.ID))
                broadcastOption.text = unicode(broadcast)
                if broadcast is self.broadcast:
                    broadcastOption.set(u"selected", u"selected")
                
                found = True
        ok = self.input(parent, type=u"submit", name=u"updateBroadcast", value=u"Apply")
        if found is None:
            ok.tail = u" (no suitable broadcasts found at the given timestamp)"
        
        newBroadcast = self.SubElement(parent, u"div")
        if self.broadcast is not None:
            newBroadcast.set(u"class", u"hidden")
            newBroadcast.tail = u"Reusing the frequencies assigned to the selected broadcast. If you want different frequencies, you must create a new broadcast."
        newBroadcast.text = u"Frequencies: "
        
        freqTable = self._frequencyTable(newBroadcast)
        
        self.br(newBroadcast)
        self.input(newBroadcast, type=u"checkbox", name=u"broadcastConfirmed", id=u"broadcastConfirmed", attrib={
            u"checked": u"checked"
        } if self.broadcastConfirmed else {})
        self.SubElement(newBroadcast, u"label", attrib={
            u"for": u"broadcastConfirmed"
        }).text = u" confirmed"
        
        self.br(newBroadcast, u"Comment: ")
        self.input(newBroadcast, name=u"broadcastComment", value=self.broadcastComment, style=u"width: 100%;")
        
        self.br(parent, u"Silence before TX (only for channelmarker-stations): ")
        self.input(parent, name=u"broadcastBefore", value=unicode(self.broadcastBefore)).tail = u" s"
        
        self.br(parent, u"Silence after TX (only for channelmarker-stations): ")
        self.input(parent, name=u"broadcastAfter", value=unicode(self.broadcastAfter)).tail = u" s"
        
    def _contentsTree(self, parent):
        parent[0].tail = u"Transmission class: "
        classSelect = self.SubElement(parent, u"select", name=u"transmissionClass")
        for txClass in self.store.find(TransmissionClass).order_by(Asc(TransmissionClass.DisplayName)):
            option = self.SubElement(classSelect, u"option", value=unicode(txClass.ID))
            option.text = txClass.DisplayName
            if txClass is self.txClass:
                option.set(u"selected", u"selected")
        
        text = self.SubElement(parent, u"textarea", rows=u"5", style=u"width: 100%", name=u"transmissionRaw")
        text.text = self.transmissionRaw
        
        parseTx = self.input(parent, type=u"submit", name=u"parseTx", value=u"Check transmission")
        
        if self.txClass is not None:
            items = None
            status = u""
            try:
                items = txClass.parsePlainText(self.transmissionRaw)
            except ValueError as e:
                status = u"Parsing failed: {0:s}".format(e)
            except NodeError as e:
                status = u"Parsing failed: {0:s}".format(e)
            if items is not None:
                if len(items) > 0:
                    status = u"Parsing ok, creates {0:d} items.".format(len(items))
                else:
                    status = u"Parsing failed, no items"
            else:
                status = u"Parsing failed, parser returned None."
            parseTx.tail = status
        else:
            parseTx.tail = u"Select a transmission class and hit Check transmission to validate your input before submitting!"
        
    def insert(self):
        # most of the prework has been done already, only need to take some minor validations
        # lets go strict:
        self.station = self.getQueryValue("station", self.stationValidator)
        self.txClass = self.getQueryValue("transmissionClass", self.transmissionClassValidator)
        
        frequencies = [(BroadcastFrequency.parseFrequency(item["frequency"]), item["modulation"]) for key, item in self.queryEx["frequencies"].iteritems() if key != "new"]
        
        if self.error is not None:
            self.setError(self.error)
        
        timestamp = TimeUtils.toTimestamp(self.timestamp)
        if self.broadcast is not None:
            if abs(timestamp - broadcast.BroadcastStart) > 600:
                self.setError(u"Cannot use this broadcast: It is more than one minute away from transmission time.")
        
        try:
            contents = self.txClass.parsePlainText(self.transmissionRaw)
        except ValueError as e:
            self.setError(unicode(e))
        except NodeError as e:
            self.setError(unicode(e))
        
        if self.broadcast is None:
            self.broadcast = Broadcast()
            self.broadcast.BroadcastStart = timestamp - self.broadcastBefore
            self.broadcast.BroadcastEnd = timestamp + self.duration + self.broadcastAfter
            self.broadcast.Comment = self.broadcastComment
            self.broadcast.Type = u"data"
            self.broadcast.Confirmed = self.broadcastConfirmed
            self.broadcast.Station = self.station
            
            for frequency, modulation in frequencies:
                freq = BroadcastFrequency()
                freq.Frequency = frequency
                mod = self.store.find(Modulation, Modulation.Name == modulation).any()
                if mod is None:
                    mod = Modulation()
                    mod.Name = modulation
                    self.store.add(mod)
                freq.Modulation = mod
                freq.Broadcast = self.broadcast
                self.store.add(freq)
            
            self.store.add(self.broadcast)
        else:
            if self.broadcast.BroadcastStart > timestamp:
                self.broadcast.BroadcastStart = timestamp - self.broadcastBefore
            else:
                self.broadcast.BroadcastEnd = timestamp + duration + self.broadcastAfter
        
        transmission = Transmission()
        transmission.Broadcast = self.broadcast
        transmission.Class = self.txClass
        self.store.add(transmission)
        transmission.__storm_loaded__()
        transmission.Callsign = self.callsign
        transmission.ForeignCallsign.supplement.LangCode = self.foreignCallsignLang
        transmission.ForeignCallsign.supplement.ForeignText = self.foreignCallsign
        transmission.Remarks = self.remarks
        transmission.Timestamp = timestamp
        transmission.RecordingURL = self.recordingURL
        
        for order, rowData in itertools.izip(xrange(len(contents)), contents):
            tableClass = rowData[0].PythonClass
            contentDict = rowData[1]
            
            row = tableClass(self.store)
            row.Transmission = transmission
            row.Order = order
            
            for key, (value, foreign) in contentDict.iteritems():
                setattr(row, key, value)
                if foreign is not None:
                    supplement = row.supplements[key].supplement
                    supplement.LangCode = foreign[0]
                    supplement.ForeignText = foreign[1]
        
        transmission.updateBlocks()
        self.store.commit()
        
        self.SubElement(self.body, u"pre").text = u"""Added transmission
Station: {0}
Broadcast (#{2}): {1}
Transmission (#{4}): {3}""".format(
            unicode(transmission.Broadcast.Station),
            unicode(transmission.Broadcast),
            unicode(transmission.Broadcast.ID),
            unicode(transmission),
            unicode(transmission.ID)
        )
        
    def buildDoc(self, trans, elements):
        self.modulationSelector = None # make sure its regenerated each request
        
        try:
            self.station = self.getQueryValue("station", self.stationValidator, defaultKey=None)
            #self.broadcast = 
            self.timestamp = self.getQueryValue("timestamp", self.timestampValidator, defaultKey=TimeUtils.nowDate(), default=None)
            self.duration = self.getQueryValue("duration", self.durationValidator, defaultKey=0.)
            self.callsign = self.getQueryValue("callsign", self.unicodeValidator, defaultKey=u"")
            self.foreignCallsignLang = self.getQueryValue("foreignCallsign[lang]", self.unicodeValidator, defaultKey=u"")
            self.foreignCallsign = self.getQueryValue("foreignCallsign[value]", self.unicodeValidator, defaultKey=u"")
            self.remarks = self.getQueryValue("remarks", self.unicodeValidator, defaultKey=u"")
            self.recordingURL = self.getQueryValue("recording", self.unicodeValidator, defaultKey=u"")
            
            self.broadcast = self.getQueryValue("broadcast", self.broadcastValidator, defaultKey=None)
            if self.broadcast == u"":
                self.broadcast = None
            self.broadcastBefore = self.getQueryValue("broadcastBefore", self.durationValidator, defaultKey=0.)
            self.broadcastAfter = self.getQueryValue("broadcastAfter", self.durationValidator, defaultKey=0.)
            self.broadcastConfirmed = self.getQueryValue("broadcastConfirmed", unicode, default=None) is not None
            self.broadcastComment = self.getQueryValue("broadcastComment", self.unicodeValidator, defaultKey=u"")
            
            self.txClass = self.getQueryValue("transmissionClass", self.transmissionClassValidator, defaultKey=None)
            self.transmissionRaw = self.getQueryValue("transmissionRaw", self.unicodeValidator, defaultKey=u"")
        except SubmitParameterError:
            pass
        
        self.queryEx = self.parseQueryDict()
        
        self.error = u""
        
        self.setTitle(u"Submit logs")
        self.link(u"/css/submit.css")
        
        submitted = False
        if "submit" in self.queryEx and self.error is None:
            try:
                self.insert()
                submitted = True
            except SubmitParameterError:
                submitted = False
        
        if not submitted:
            self.SubElement(self.body, u"pre").text = self.recursiveDict(self.queryEx)
            if len(self.error) > 0:
                self.SubElement(error, u"div").text = self.error
                
            form = self.SubElement(self.body, u"form", name=u"logform", method=u"POST")
            
            self._basicInformationTree(self.section(form, u"Basic information"))
            self._broadcastTree(self.section(form, u"Broadcast"))
            self._contentsTree(self.section(form, u"Transmission contents"))
            
            self.SubElement(form, u"input", type=u"submit", name=u"submit", value=u"Submit")
