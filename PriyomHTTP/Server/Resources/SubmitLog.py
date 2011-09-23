from WebStack.Generic import ContentType, EndOfResponse
from Resource import Resource
from libPriyom import *

class SubmitLogResource(Resource):
    def __init__(self, model):
        super(SubmitLogResource, self).__init__(model)
        self.allowedMethods = frozenset(["GET", "POST"])
    
    def handle(self, trans):
        trans.set_content_type(ContentType("text/html", self.encoding))
        
        stations = self.store.find(Station)
        stationId = self.getQueryIntDefault("stationId", None)
        
        print >>self.out, (u"""<!DOCTYPE HTML>
<html>
    <head>
        <title>{1}</title>
        <link rel="stylesheet" type="text/css" href="{0}{2}" />
        <script src="{0}{3}" type="text/javascript">
        </script>
    </head>
    <body>
        <form name="logform" action="submit" method="POST">
            Station: <select name="stationId">
                {4}
            </select><br />
            
            <input type="submit" name="submit" value="Submit logs" />
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
                                        ) for station in stations))
        ).encode(self.encoding, 'replace')
