# encoding=utf-8
from storm.locals import *
from WebStack.Generic import ContentType, EndOfResponse
from Resource import Resource
from libPriyom import *
from datetime import datetime, timedelta
from time import mktime, time
import re

freqRe = re.compile("([0-9]+(\.[0-9]*)?|\.[0-9]+)\s*(([mkg]?)hz)?", re.I)
siPrefixes = {
    "" : 1,
    "k": 1000,
    "m": 1000000,
    "g": 1000000000
}

class SubmitLogResource(Resource):
    def __init__(self, model):
        super(SubmitLogResource, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
        
    def parseFrequency(self, freqStr):
        global freqRe
        m = freqRe.match(freqStr)
        if m is None:
            return None
        si = m.group(4)
        return float(m.group(1)) * siPrefixes[si.lower() if si is not None else ""]
        
    def formatFrequency(self, freq):
        freq = int(freq)
        if freq > 1000000000:
            return unicode((freq / 1000000000.0)) + u" GHz"
        elif freq > 1000000:
            return unicode((freq / 1000000.0)) + u" MHz"
        elif freq > 1000:
            return unicode((freq / 1000.0)) + u" kHz"
        else:
            return unicode(freq) + u" Hz"
        
    def formatFrequencies(self):
        i = -1
        items = [(key, value) for key, value in self.queryEx.get("frequencies", {}).iteritems() if (key != "new" or "submit" in value) and (not "delete" in value)]
        items.sort(lambda x,y: cmp(x[0], y[0]))
        for key, item in items:
            i += 1
            if "submit" in item:
                item["frequency"] = "0 Hz"
                item["modulation"] = "USB"
            freq = self.parseFrequency(item["frequency"])
            if freq is None:
                freq = "0 Hz"
            else:
                freq = self.formatFrequency(freq)
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
        for broadcast in (self.model.priyomInterface.getCloseBroadcasts(station.ID, timestamp, 600)[1]):
            if broadcast.Type == u"continous":
                continue
            ids.append(broadcast.ID)
            yield u"""<option value="{0}"{3}>Broadcast at {1} on {2}</option>""".format(
                broadcast.ID,
                datetime.fromtimestamp(broadcast.BroadcastStart).strftime(Formatting.priyomdate),
                u", ".join((self.formatFrequency(freq.Frequency) for freq in broadcast.Frequencies)),
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
            Silence after TX: <input type="text" name="broadcastAfter" value="{1}" /> seconds""".format(
            self.queryEx.get("broadcastBefore", 0),
            self.queryEx.get("broadcastAfter", 0)
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
        
        
        timestamp = self.queryEx.get("timestamp", None)
        if timestamp is None:
            timestamp = self.model.now()
        else:
            try:
                timestamp = self.model.priyomInterface.toTimestamp(datetime.strptime(timestamp, Formatting.priyomdate))
            except ValueError:
                timestamp = self.model.now()
        
        print >>self.out, (u"""
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <title>{1}</title>
        <link rel="stylesheet" type="text/css" href="{0}{2}" />
        <script src="{0}{3}" type="text/javascript" />
    </head>
    <body>
        <form name="logform" action="submit" method="POST">
            <div class="section">
                <div class="inner-caption">Basic information</div>
                Station: <select name="stationId">
                    {4}
                </select><br />
                Timestamp: <input type="text" name="timestamp" value="{5}" /><br />
                Duration: <input type="text" name="duration" value="{8}" /> seconds<br />
                Remarks: <input type="text" name="remarks" value="{10}" style="width: 100%" />
            </div>
            {6}
            <div class="section">
                <div class="inner-caption">Transmission contents:</div>
                {9}
            </div>
            <input type="submit" name="submit" value="Submit" />
        </form>
    </body>
</html>""").format(
            self.model.rootPath(u""),
            self.model.formatHTMLTitle(u"Submit logs"),
            u"/css/submit.css",
            u"/js/jquery.js",
            u"\n                ".join((u"""<option value="{0}"{1}>{3}{4}{2}</option>""".format(
                                            station.ID,
                                            u' selected="selected"' if station.ID == stationId else u"",
                                            u" (" + station.Nickname + u")" if len(station.Nickname) > 0 else u"",
                                            station.EnigmaIdentifier + (u" / " if len(station.EnigmaIdentifier) > 0 and len(station.PriyomIdentifier) > 0 else u""),
                                            station.PriyomIdentifier
                                        ) for station in stations)),
            datetime.fromtimestamp(timestamp).strftime(Formatting.priyomdate),
            u"\n            ".join(self.formatBroadcastSelector(station, timestamp)),
            u"",# self.recursiveDict(self.queryEx),
            self.queryEx.get("duration", 0),
            u"\n            ".join(self.formatTransmissionEditor()),
            self.queryEx.get("remarks", "")
        ).encode(self.encoding, 'replace')
