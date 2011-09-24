# encoding=utf-8
from storm.locals import *
from WebStack.Generic import ContentType, EndOfResponse
from Resource import Resource
from libPriyom import *
from datetime import datetime, timedelta
from time import mktime, time

class SubmitLogResource(Resource):
    def __init__(self, model):
        super(SubmitLogResource, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
        
    def formatFrequencies(self):
        i = -1
        items = [(key, value) for key, value in self.queryEx.get("frequencies", {}).iteritems() if (key != "new" or "submit" in value) and (not "delete" in value)]
        items.sort(lambda x,y: cmp(x[0], y[0]))
        for key, item in items:
            i += 1
            if "submit" in item:
                item["frequency"] = "0 Hz"
                item["modulation"] = "USB"
            freq = BroadcastFrequency.parseFrequency(item["frequency"])
            if freq is None:
                freq = "0 Hz"
            else:
                freq = BroadcastFrequency.formatFrequency(freq)
            yield u"""<tr>
    <td><input type="text" name="frequencies[{0}][frequency]" value="{1}" /></td>
    <td><select name="frequencies[{0}][modulation]">{2}</select></td>
    <td class="buttons"><input type="submit" name="frequencies[{0}][update]" value="Save" /><input type="submit" name="frequencies[{0}][delete]" value="✗" /></td>
</tr>""".format(
                unicode(i),
                freq,
                u"\n".join((u"""<option value="{0}"{1}>{0}</option>""".format(modulation.Name, u' selected="selected"' if modulation.Name == item["modulation"] else u"") for modulation in self.store.find(Modulation).order_by(Asc(Modulation.Name))))
            )
        item = self.queryEx.get("frequencies", {}).get("new", {"frequency": "10 MHz", "modulation": "USB"})
        yield u"""<tr>
    <td class="buttons" colspan="3"><input type="submit" name="frequencies[new][submit]" value="+" /></td>
</tr>""".format(
            item["frequency"],
            u"\n".join((u"""<option value="{0}"{1}>{0}</option>""".format(modulation.Name, u' selected="selected"' if modulation.Name == item["modulation"] else u"") for modulation in self.store.find(Modulation).order_by(Asc(Modulation.Name))))
        )
        
    def formatBroadcastSelector(self, station, timestamp):
        yield u"""<div class="section">"""
        yield u"""<div class="inner-caption">Broadcast: </div>"""
        yield u"""<select name="broadcast">"""
        yield u"""<option value="0">New broadcast</option>"""
        found = False
        ids = list()
        if station is not None:
            for broadcast in (self.model.priyomInterface.getCloseBroadcasts(station.ID, timestamp, 600)[1]):
                if broadcast.Type == u"continous":
                    continue
                ids.append(broadcast.ID)
                yield u"""<option value="{0}"{2}>{1}</option>""".format(
                    broadcast.ID,
                    unicode(broadcast),
                    u' selected="selected"' if broadcast.ID == int(self.queryEx.get("broadcast", 0)) else u""
                )
                found = True
        yield u"""</select><input type="submit" name="updateBroadcast" value="Ok" />"""
        
        if not found:
            yield u""" (no suitable broadcasts found at the given timestamp)"""
        
        if not found or not "broadcast" in self.queryEx or self.queryEx["broadcast"] == "0":
            yield u"""<div>"""
        else:
            yield u"""<div class="hidden">"""

        yield u"""Frequencies:
            <table class="frequency-table">
                <thead>
                    <th>Frequency</th>
                    <th>Modulation/Mode</th>
                    <th class="buttons"></th>
                </thead>
                <tbody>"""
            
        for line in self.formatFrequencies():
            yield line
            
        yield u"""
                </tbody>
            </table>
            Silence before TX: <input type="text" name="broadcastBefore" value="{0}" /> seconds<br />
            Silence after TX: <input type="text" name="broadcastAfter" value="{1}" /> seconds<br />
            <input type="checkbox" name="broadcastConfirmed"{3} id="broadcastConfirmed" /><label for="broadcastConfirmed"> confirmed</label><br />
            Comment: <input type="text" name="broadcastComment" value="{2}" style="width: 100%;" /><br />""".format(
            self.queryEx.get("broadcastBefore", 0),
            self.queryEx.get("broadcastAfter", 0),
            self.queryEx.get("broadcastComment", u""),
            u' checked="checked"' if "broadcastConfirmed" in self.queryEx else u""
        )
            
        yield u"""</div></div>"""
        
    def recursiveDictNode(self, dictionary, indent = u""):
        for key, value in dictionary.iteritems():
            if type(value) == dict:
                yield u"""{1}{0}: {2}""".format(key, indent, u"{")
                for line in self.recursiveDictNode(value, indent + u"    "):
                    yield line
                yield u"""{0}{1}""".format(indent, u"}")
            else:
                yield u"""{2}{0}: {1}""".format(key, repr(value), indent)
        
    def recursiveDict(self, dict):
        return "\n".join(self.recursiveDictNode(dict))
        
    def formatTransmissionEditor(self):
        yield u"""Transmission class: <select name="transmissionClass">"""
        txClassId = int(self.queryEx.get("transmissionClass", 0))
        for txClass in self.store.find(TransmissionClass).order_by(Asc(TransmissionClass.DisplayName)):
            yield u"""<option value="{0}"{2}>{1}</option>""".format(
                txClass.ID,
                txClass.DisplayName,
                u' selected="selected"' if txClass.ID == txClassId else u""
            )
        yield u"""</select>"""
        yield u"""<textarea name="transmission" rows="5" style="width: 100%">{0}</textarea>""".format(self.queryEx.get("transmission", u""))
        yield u"""<input type="submit" name="parseTx" value="Check transmission" />"""
        
        txClass = self.store.get(TransmissionClass, txClassId)
        if txClass is not None:
            items = None
            try:
                items = txClass.parsePlainText(self.queryEx.get("transmission", u""))
            except ValueError as e:
                yield u""" Parsing failed: {0:s}""".format(e)
            except NodeError as e:
                yield u""" Parsing failed: {0:s}""".format(e)
            if items is not None:
                if len(items) > 0:
                    yield u""" Parsing ok, creates {0:d} items.""".format(len(items))
                else:
                    yield u""" Parsing failed, no items"""
                    
    def insert(self):
        try:
            station = self.store.get(Station, int(self.queryEx["stationId"]))
            if station is None:
                raise KeyError("No station with id #{0}".format(self.queryEx["stationId"]))
            timestamp = self.queryEx["timestamp"]
            duration = int(self.queryEx["duration"])
            remarks = self.queryEx["remarks"]
            callsign = self.queryEx["callsign"]
            foreignCallsignLang = self.queryEx["foreignCallsign"]["lang"]
            foreignCallsign = self.queryEx["foreignCallsign"]["value"]
            if len(foreignCallsign) != 0 and len(foreignCallsignLang) == 0:
                raise KeyError("Foreign callsign given but no language code set.")
            
            broadcast = self.store.get(Broadcast, int(self.queryEx["broadcast"]))
            if broadcast is None and int(self.queryEx["broadcast"]) != 0:
                raise KeyError("No broadcast with id #{0}".format(self.queryEx["broadcast"]))
            broadcastAfter = int(self.queryEx["broadcastAfter"])
            broadcastBefore = int(self.queryEx["broadcastBefore"])
            broadcastFrequencies = [(BroadcastFrequency.parseFrequency(item["frequency"]), item["modulation"]) for key, item in self.queryEx["frequencies"].iteritems() if key != "new"]
            broadcastConfirmed = "broadcastConfirmed" in self.queryEx
            broadcastComment = self.queryEx["broadcastComment"]
            
            transmissionClass = self.store.get(TransmissionClass, int(self.queryEx["transmissionClass"]))
            if transmissionClass is None:
                raise KeyError("No transmission class with id #{0}".format(self.queryEx["transmissionClass"]))
            transmissionContents = self.queryEx["transmission"]
            
            if timestamp is None:
                timestamp = self.model.now()
            else:
                try:
                    timestamp = self.model.priyomInterface.toTimestamp(datetime.strptime(timestamp, Formatting.priyomdate))
                except ValueError:
                    timestamp = self.model.now()
        except KeyError as e:
            return unicode(e)
            
        if broadcast is None:
            broadcast = Broadcast()
            self.store.add(broadcast)
            broadcast.BroadcastStart = timestamp - broadcastBefore
            broadcast.BroadcastEnd = timestamp + duration + broadcastAfter
            broadcast.Comment = broadcastComment
            broadcast.Type = u"data"
            broadcast.Confirmed = broadcastConfirmed
            broadcast.Station = station
            
            for freqItem in broadcastFrequencies:
                freq = BroadcastFrequency()
                self.store.add(freq)
                freq.Frequency = freqItem[0]
                modulation = self.store.find(Modulation, Modulation.Name == freqItem[1]).any()
                if modulation is None:
                    modulation = Modulation()
                    modulation.Name = freqItem[1]
                    self.store.add(modulation)
                freq.Modulation = modulation
                freq.Broadcast = broadcast
        else:
            if broadcast.BroadcastStart > timestamp:
                broadcast.BroadcastStart = timestamp
            else:
                broadcast.BroadcastEnd = timestamp + duration
                
        transmission = Transmission()
        self.store.add(transmission)
        transmission.Broadcast = broadcast
        transmission.Class = transmissionClass
        transmission.__storm_loaded__()
        transmission.Callsign = callsign
        transmission.ForeignCallsign.supplement.LangCode = foreignCallsignLang
        transmission.ForeignCallsign.supplement.ForeignText = foreignCallsignLang
        transmission.Remarks = remarks
        transmission.Timestamp = timestamp
        transmission.RecordingURL = None
        
        contents = transmissionClass.parsePlainText(transmissionContents)
        order = 0
        for rowData in contents:
            tableClass = rowData[0].PythonClass
            contentDict = rowData[1]
            
            row = tableClass(self.store)
            row.Transmission = transmission
            row.Order = order
            
            for key, value in contentDict.iteritems():
                foreign = value[1]
                value = value[0]
                setattr(row, key, value)
                if foreign is not None:
                    row.supplements[key].LangCode = foreign[0]
                    row.supplements[key].ForeignText = foreign[0]
            
            order += 1
            
        transmission.updateBlocks()
        self.store.flush()
        
        print >>self.out, u"""<pre>Added transmission
Station: {0}
Broadcast: {1}
Transmission: {2}</pre>""".format(
            unicode(transmission.Broadcast.Station),
            unicode(transmission.Broadcast),
            unicode(transmission)
        )
        
    
    def handle(self, trans):
        trans.set_content_type(ContentType(self.xhtmlContentType, self.encoding))
        
        stations = self.store.find(Station).order_by(Asc(Station.EnigmaIdentifier), Asc(Station.PriyomIdentifier), Asc(Station.Nickname))
        station = self.store.get(Station, self.getQueryIntDefault("stationId", 0))
        if station is not None:
            stationId = station.ID
        else:
            stationId = None
        
        broadcast = self.store.get(Broadcast, self.getQueryIntDefault("broadcastId", 0))
        broadcastSet = broadcast is not None
        
        self.queryEx = self.parseQueryDict()
        
        error = u""
        
        timestamp = self.queryEx.get("timestamp", None)
        if timestamp is None:
            timestamp = self.model.now()
        else:
            try:
                timestamp = self.model.priyomInterface.toTimestamp(datetime.strptime(timestamp, Formatting.priyomdate))
            except ValueError:
                timestamp = self.model.now()
        
        print >>self.out, u"""<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>{1}</title>
        <link rel="stylesheet" type="text/css" href="{0}{2}" />
        <script src="{0}{3}" type="text/javascript" />
    </head>
    <body>""".format(            
            self.model.rootPath(u""),
            self.model.formatHTMLTitle(u"Submit logs"),
            u"/css/submit.css",
            u"/js/jquery.js"
        ).encode(self.encoding, 'replace')
        
        submitted = False
        if "submit" in self.queryEx:
            insertResult = self.insert()
            if insertResult is not None:
                error = insertResult
            else:
                submitted = True
        
        if not submitted:
            print >>self.out, u"""
        <form name="logform" action="submit" method="POST">
            <pre>{3}</pre>
            {7}
            <div class="section">
                <div class="inner-caption">Basic information</div>
                Station: <select name="stationId">
                    {0}
                </select><br />
                Timestamp: <input type="text" name="timestamp" value="{1}" /><br />
                Duration: <input type="text" name="duration" value="{4}" /> seconds<br />
                Callsign: <input type="text" name="callsign" value="{8}" /> <br />
                Foreign callsign language code: <input type="text" name="foreignCallsign[lang]" value="{9}" /><br />
                Foreign callsign: <input type="text" name="foreignCallsign[value]" value="{10}" /><br />
                Remarks: <input type="text" name="remarks" value="{6}" style="width: 100%" />
            </div>
            {2}
            <div class="section">
                <div class="inner-caption">Transmission contents:</div>
                {5}
            </div>
            <input type="submit" name="submit" value="Submit" />
        </form>""".format(
                u"\n                ".join((u"""<option value="{0}"{1}>{2}</option>""".format(
                                                station.ID,
                                                u' selected="selected"' if station.ID == stationId else u"",
                                                unicode(station)
                                            ) for station in stations)),
                datetime.fromtimestamp(timestamp).strftime(Formatting.priyomdate),
                u"\n            ".join(self.formatBroadcastSelector(station, timestamp)),
                self.recursiveDict(self.queryEx),
                self.queryEx.get("duration", 0),
                u"\n            ".join(self.formatTransmissionEditor()),
                self.queryEx.get("remarks", u""),
                u'<div class="error">{0}</div>'.format(error) if len(error) > 0 else u"",
                self.queryEx.get("callsign", u""),
                self.queryEx.get("foreignCallsign", {}).get("lang", u""),
                self.queryEx.get("foreignCallsign", {}).get("value", u"")
            ).encode(self.encoding, 'replace')
            
        print >>self.out, u"""
    </body>
</html>""".encode(self.encoding, 'replace')
