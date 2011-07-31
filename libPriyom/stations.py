from storm.locals import *
import xmlintf
import schedules
import transmissions
import imports
import broadcasts
import xml.dom.minidom as dom

class Station(xmlintf.XMLStorm):
    __storm_table__ = "stations"
    ID = Int(primary = True)
    EnigmaIdentifier = Unicode()
    PriyomIdentifier = Unicode()
    Nickname = Unicode()
    Description = Unicode()
    Status = Unicode()
    Location = Unicode()
    ScheduleID = Int()
    Schedule = Reference(ScheduleID, schedules.Schedule.ID)
    ScheduleConfirmed = Bool()
    ScheduleUpToDateUntil = Int()
    
    xmlMapping = {
        u"enigma-id": "EnigmaIdentifier",
        u"priyom-id": "PriyomIdentifier",
        u"nickname": "Nickname",
        u"description": "Description",
        u"status": "Status",
        u"location": "Location"
    }
    
    def _metadataToDom(self, doc, parentNode):
        metadata = doc.createElementNS(xmlintf.namespace, "station-metadata")
        xmlintf.appendTextElements(metadata,
            [
                ("enigma-id", self.EnigmaIdentifier),
                ("priyom-id", self.PriyomIdentifier),
                ("nickname", self.Nickname),
                ("description", self.Description),
                ("status", self.Status)
            ],
            noneHandler = lambda name: ""
        )
        if self.Location is not None:
            xmlintf.appendTextElement(metadata, "location", self.Location)
        if self.getIsOnAir():
            metadata.appendChild(doc.createElementNS(xmlintf.namespace, "on-air"))
        parentNode.appendChild(metadata)
        
    def _broadcastsFromDom(self, node):
        for child in node.childNodes:
            if child.nodeType != dom.Node.ELEMENT_NODE:
                continue
            if child.tagName == "broadcast":
                broadcast = imports.importSimple(Store.of(self), broadcasts.Broadcast, child)
                if broadcast.Station != self and broadcast.ScheduleLeaf is not None and broadcast.ScheduleLeaf.Station != self:
                    print("Cannot reassign a broadcast which is bound to a schedule leaf which is not assigned to target station.")
                else:
                    broadcast.Station = self
        
    def _transmissionsFromDom(self, node):
        print("Cannot import transmissions using station import. Please import transmissions directly or as part of broadcast imports.")
        pass
        
    def _scheduleFromDom(self, node):
        self.Schedule = imports.importSimple(Store.of(self), Schedule, node)
        self.ScheduleConfirmed = node.getAttribute("confirmed") == "true"
        
    def loadDomElement(self, node):
        try:
            {
                "station-metadata": self.loadProperties,
                "broadcasts": self._broadcastsFromDom,
                "transmissions": self._transmissionsFromDom,
                "schedule": self._scheduleFromDom
            }[node.tagName](node)
        except KeyError:
            pass
        
    def fromDom(self, node):
        self.loadProperties(node)
        
    def getIsOnAir(self):
        return False
    
    def toDom(self, parentNode, flags = None):
        doc = parentNode.ownerDocument
        station = doc.createElementNS(xmlintf.namespace, "station")
        xmlintf.appendTextElement(station, "id", unicode(self.ID))
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
                scheduleNode = doc.createElementNS(xmlintf.namespace, "schedule")
                scheduleNode.setAttribute("confirmed", "true")
                station.appendChild(scheduleNode)
            
        if flags is None or "broadcasts" in flags:
            broadcasts = doc.createElementNS(xmlintf.namespace, "broadcasts")
            for broadcast in self.Broadcasts:
                broadcast.toDom(broadcasts, flags)
            station.appendChild(broadcasts)
        
        if flags is None or ("transmissions" in flags and not ("broadcasts" in flags and "broadcast-transmissions" in flags)):
            transmissions = doc.createElementNS(xmlintf.namespace, "transmissions")
            for transmission in self.Transmissions:
                transmission.toDom(transmissions, flags)
            station.appendChild(transmissions)
        
        parentNode.appendChild(station)
        
    def __str__(self):
        return "Station: %s/%s \"%s\"" % (self.EnigmaIdentifier, self.PriyomIdentifier, self.Nickname)
