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
        
    def formatFrequencies(self, editable):
        yield u"""<tr>
    <td><input type="text" name="frequencies[new][frequency]" value="0" /></td>
    <td><input type="text" name="frequencies[new][modulation]" value="" /></td>
    <td><input type="submit" name="frequencies[new][submit]" value="+" /></td>
</tr>"""
    
    def handle(self, trans):
        trans.set_content_type(ContentType(self.xhtmlContentType, self.encoding))
        
        stations = self.store.find(Station).order_by(Asc(Station.EnigmaIdentifier), Asc(Station.PriyomIdentifier), Asc(Station.Nickname))
        stationId = self.getQueryIntDefault("stationId", None)
        
        broadcast = self.store.get(Broadcast, self.getQueryIntDefault("broadcastId", 0))
        
        broadcastSet = broadcast is not None
        
        if "submit" in self.query:
            raise Exception(self.query)
        
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
            Frequencies:
            <table class="frequency-table">
                <thead>
                    <th>Frequency (Hz)</th>
                    <th>Modulation/Mode</th>
                </thead>
                <tbody>
                    {6}
                </tbody>
            </table>
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
            datetime.utcnow().strftime(Formatting.priyomdate),
            u"\n                    ".join(iter(self.formatFrequencies(not broadcastSet)))
        ).encode(self.encoding, 'replace')
