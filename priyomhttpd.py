#!/usr/bin/python2.7
from storm.locals import *
import BaseHTTPServer
import libpriyom.interface
import priyomhttp.server
import priyomhttp.server.servlets as servlets
from priyomhttp.server.CommandNamespaces import ExportMethod, ExportNamespace, MethodArgumentMapping, DefaultArguments, invFlagCast, flagCast, flagsCast, commaList, intRange

db = create_database("mysql://priyom@localhost/priyom")
store = Store(db)
iface = libpriyom.interface.PriyomInterface(store)
priyomhttp.server.servlets.priyomInterface = iface

priyomhttp.server.PriyomHTTPRequestHandler.exports = ExportMethod(
    servlets.get('empty').empty,
    exports = {
        'broadcasts': ExportNamespace({
            "get": ExportMethod(
                servlets.get('broadcast').getById,
                {
                    "id": MethodArgumentMapping("args", 0, int, 
                        description="ID of the broadcast to fetch'")
                },
                {                    
                    "flags": DefaultArguments.flags,
                },
                exports = {
                    "upcoming": ExportMethod(
                        servlets.get('broadcasts').getUpcoming, 
                        {},
                        {
                            "timeLimit": MethodArgumentMapping("kwargs", "timeLimit", int, 
                                description="Time limit in seconds from now up to which broadcasts will be looked up."),
                            "no-update": MethodArgumentMapping("kwargs", "update", invFlagCast(), 
                                description="If set, no broadcasts will be instantiated from schedules. This reduces the server load, but information may be inaccurate then."),
                            "all": MethodArgumentMapping("kwargs", "all", flagCast(),
                                description="Also return continous broadcasts."),
                            "stationId": MethodArgumentMapping("kwargs", "stationId", int,
                                description="Restrict query to one specific station."),
                            "flags": DefaultArguments.flags,
                            "offset": DefaultArguments.offset,
                            "limit": DefaultArguments.limit,
                            "distinct": DefaultArguments.distinct,
                        }
                    ),
                    "byFrequency": ExportMethod(
                        servlets.get('broadcasts').getByFrequency,
                        {
                            "frequency": MethodArgumentMapping("args", 0, intRange(), 
                                description="The frequency (range) to look for.")
                        },
                        {
                            "modulation": MethodArgumentMapping("kwargs", "modulation", unicode, 
                                description="If specified, this method will only return broadcasts which used (or use) the given modulation."),
                            "flags": DefaultArguments.flags,
                            "offset": DefaultArguments.offset,
                            "limit": DefaultArguments.limit,
                            "distinct": DefaultArguments.distinct,
                        }
                    )
                }
            )
        }),
        'stations': ExportNamespace({
            "get": ExportMethod(
                servlets.get('station').getById,
                {
                    "id": MethodArgumentMapping("args", 0, int, 
                        description="ID of the station to fetch'")
                },
                {                    
                    "flags": DefaultArguments.flags,
                },
                exports = {
                    "byPriyomIdentifier": ExportMethod(
                        servlets.get('station').getByPriyomId,
                        {
                            "pid": MethodArgumentMapping("args", 0, unicode, 
                                description="Priyom identifier of the station to fetch.")
                        },
                        {                    
                            "flags": DefaultArguments.flags,
                        }
                    ),
                    "byEnigmaIdentifier": ExportMethod(
                        servlets.get('station').getByEnigmaId,
                        {
                            "eid": MethodArgumentMapping("args", 0, unicode, 
                                description="Enigma identifier of the station to fetch.")
                        },
                        {                    
                            "flags": DefaultArguments.flags,
                        }
                    )
                }
            ),
            "list": ExportMethod(
                servlets.get('stations').list,
                {
                },
                {
                    "ids": MethodArgumentMapping("kwargs", "idList", commaList("comma separated list of IDs", int), 
                        description="If given, only the stations with the given IDs will be returned."),
                    "strict": MethodArgumentMapping("kwargs", "strict", flagCast(), 
                        description="If set, a 404 will be returned if not all IDs exist."),
                    "offset": DefaultArguments.offset,
                    "limit": DefaultArguments.limit,
                    "distinct": DefaultArguments.distinct,
                }
            ),
            "find": ExportMethod(
                servlets.get('stations').find,
                {
                    "field": MethodArgumentMapping("args", 0, unicode, 
                        description="Name of the field to check against."),
                    "operator": MethodArgumentMapping("args", 1, unicode,
                        description="""
                            Operator to apply. Valid operators are:
                            <ul>
                                <li>equals</li>
                                <li>like</li>
                                <li>less</li>
                                <li>greater</li>
                                <li>lequal</li>
                                <li>gequal</li>
                                <li>null</li>
                            </ul>"""),
                    "value": MethodArgumentMapping("args", 2, unicode,
                        description="Second operand for the operation. This may be empty (but not unset) if the null operator is used.")
                },
                {
                    "negate": MethodArgumentMapping("kwargs", "negate", flagCast(),
                        description="If set, the negation of the operation is applied."),
                    "offset": DefaultArguments.offset,
                    "limit": DefaultArguments.limit,
                    "distinct": DefaultArguments.distinct,
                }
            )
        })
    }
)
priyomhttp.server.setupNamespaceNames(priyomhttp.server.PriyomHTTPRequestHandler.exports)

server = BaseHTTPServer.HTTPServer(("", 8001), priyomhttp.server.PriyomHTTPRequestHandler, True)
print("Server ready.")
try:
    server.serve_forever()
except KeyboardInterrupt:
    print("KeyboardInterrupt received, terminated.")
    pass
store.flush()
