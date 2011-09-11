from storm.locals import *
import XMLIntf
from Schedule import Schedule
import Imports
from Broadcast import Broadcast
import xml.dom.minidom as dom
from PriyomBase import PriyomBase

class Station(PriyomBase, XMLIntf.XMLStorm):
    __storm_table__ = "stations"
    ID = Int(primary = True)
    BroadcastDeleted = Int()
    EnigmaIdentifier = Unicode()
    PriyomIdentifier = Unicode()
    Nickname = Unicode()
    Description = Unicode()
    Status = Unicode()
    Location = Unicode()
    ScheduleID = Int()
    Schedule = Reference(ScheduleID, Schedule.ID)
    ScheduleConfirmed = Bool()
    ScheduleUpToDateUntil = Int(default=AutoReload)
    
    xmlMapping = {
        u"EnigmaIdentifier": "EnigmaIdentifier",
        u"PriyomIdentifier": "PriyomIdentifier",
        u"Nickname": "Nickname",
        u"Description": "Description",
        u"Status": "Status",
        u"Location": "Location"
    }
    
    def _metadataToDom(self, doc, parentNode):
        #metadata = doc.createElementNS(XMLIntf.namespace, "station-metadata")
        XMLIntf.appendTextElements(parentNode,
            [
                ("EnigmaIdentifier", self.EnigmaIdentifier),
                ("PriyomIdentifier", self.PriyomIdentifier),
                ("Nickname", self.Nickname),
                ("Description", self.Description),
                ("Status", self.Status)
            ],
            noneHandler = lambda name: ""
        )
        if self.Location is not None:
            XMLIntf.appendTextElement(parentNode, "Location", self.Location)
        if self.getIsOnAir():
            parentNode.appendChild(doc.createElementNS(XMLIntf.namespace, "on-air"))
        #parentNode.appendChild(metadata)
        
    def _broadcastsFromDom(self, node, context):
        for child in node.childNodes:
            if child.nodeType != dom.Node.ELEMENT_NODE:
                continue
            if child.tagName == "broadcast":
                broadcast = context.importFromDomNode(child, Broadcast)
                if broadcast is None:
                    continue
                if broadcast.Station != self and broadcast.ScheduleLeaf is not None and broadcast.ScheduleLeaf.Station != self:
                    context.log("Cannot reassign a broadcast which is bound to a schedule leaf which is not assigned to target station.")
                else:
                    broadcast.Station = self
        
    def _transmissionsFromDom(self, node, context):
        context.log("Cannot import transmissions using station import. Please import transmissions directly or as part of broadcast imports.")
        pass
        
    def _scheduleFromDom(self, node, context):
        self.Schedule = context.importFromDomNode(node, Schedule)
        self.ScheduleConfirmed = node.getAttribute("confirmed") == "true"
        
    def loadDomElement(self, node, context):
        try:
            {
                "broadcasts": self._broadcastsFromDom,
                "transmissions": self._transmissionsFromDom,
                "schedule": self._scheduleFromDom
            }[node.tagName](node, context)
        except KeyError:
            pass
        
    def fromDom(self, node, context):
        self.loadProperties(node, context)
        
    def getIsOnAir(self):
        return False
    
    def toDom(self, parentNode, flags = None):
        doc = parentNode.ownerDocument
        station = doc.createElementNS(XMLIntf.namespace, "station")
        XMLIntf.appendTextElement(station, "ID", unicode(self.ID))
        if flags is None or not "no-metadata" in flags:
            self._metadataToDom(doc, station)
        
        if flags is None or "schedule" in flags:
            if self.Schedule is not None:
                scheduleNode = self.Schedule.toDom(station, self.ID)
                if self.ScheduleConfirmed:
                    scheduleNode.setAttribute("confirmed", "true")
                else:
                    scheduleNode.setAttribute("confirmed", "false")
            elif self.ScheduleConfirmed:
                scheduleNode = doc.createElementNS(XMLIntf.namespace, "schedule")
                scheduleNode.setAttribute("confirmed", "true")
                station.appendChild(scheduleNode)
            
        if flags is None or "broadcasts" in flags:
            broadcasts = doc.createElementNS(XMLIntf.namespace, "broadcasts")
            for broadcast in self.Broadcasts:
                broadcast.toDom(broadcasts, flags)
            station.appendChild(broadcasts)
        
        """
        if flags is None or ("transmissions" in flags and not ("broadcasts" in flags and "broadcast-transmissions" in flags)):
            transmissions = doc.createElementNS(XMLIntf.namespace, "transmissions")
            for transmission in self.Transmissions:
                transmission.toDom(transmissions, flags)
            station.appendChild(transmissions)
        """
        
        parentNode.appendChild(station)
        
    def __str__(self):
        return "Station: %s/%s \"%s\"" % (self.EnigmaIdentifier, self.PriyomIdentifier, self.Nickname)
