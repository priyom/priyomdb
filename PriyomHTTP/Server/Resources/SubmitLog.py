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
        
    def formatFrequencies(self, editable):
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
    <td><input type="submit" name="frequencies[{0}][update]" value="Save" /><input type="submit" name="frequencies[{0}][delete]" value="✗" /></td>
</tr>""".format(
                unicode(i),
                freq,
                u"\n".join((u"""<option value="{0}"{1}>{0}</option>""".format(modulation.Name, u' selected="selected"' if modulation.Name == item["modulation"] else u"") for modulation in self.store.find(Modulation).order_by(Asc(Modulation.Name))))
            )
        item = self.queryEx.get("frequencies", {}).get("new", {"frequency": "10 MHz", "modulation": "USB"})
        yield u"""<tr>
    <td colspan="3"><input type="submit" name="frequencies[new][submit]" value="+" /></td>
</tr>""".format(
            item["frequency"],
            u"\n".join((u"""<option value="{0}"{1}>{0}</option>""".format(modulation.Name, u' selected="selected"' if modulation.Name == item["modulation"] else u"") for modulation in self.store.find(Modulation).order_by(Asc(Modulation.Name))))
        )
        
    """
            Frequencies:
            <table class="frequency-table">
                <thead>
                    <th>Frequency</th>
                    <th>Modulation/Mode</th>
                </thead>
                <tbody>
                    {6}
                </tbody>
            </table>"""
        
    def formatBroadcastSelector(self, station, timestamp):
        yield u"""<select name="broadcast">"""
        yield u"""<option value="0">New broadcast</option>"""
        found = False
        ids = list()
        for broadcast in (self.model.priyomInterface.getCloseBroadcasts(station.ID, timestamp, 600)[1]):
            if broadcast.Type == u"continous":
                continue
            ids.append(broadcast.ID)
            yield u"""<option value="{0}">Broadcast at {1} on {2}</option>""".format(
                broadcast.ID,
                datetime.fromtimestamp(broadcast.BroadcastStart).strftime(Formatting.priyomdate),
                ", ".join((self.formatFrequency(freq.Frequency) for freq in broadcast.Frequencies))
            )
            found = True
        yield u"""</select>"""
        
        if not found:
            yield u""" (no suitable broadcasts found at the given timestamp)"""
        
        if not found or not "broadcast" in self.queryEx or self.queryEx["broadcast"] == "0":
            yield u"""<div>"""
        else:
            yield u"""<div class="hidden">"""
        
    
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
            Station: <select name="stationId">
                {4}
            </select><br />
            Timestamp: <input type="text" name="timestamp" value="{5}" /><br />
            Broadcast: {6}
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
            u"\n                ".join(self.formatBroadcastSelector(station, timestamp))
        ).encode(self.encoding, 'replace')
