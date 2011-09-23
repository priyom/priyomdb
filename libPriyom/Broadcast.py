from storm.locals import *
import XMLIntf
from Modulation import Modulation
import datetime
from PriyomBase import PriyomBase, now

class BroadcastFrequency(object):
    __storm_table__ = "broadcastFrequencies"
    ID = Int(primary = True)
    BroadcastID = Int()
    Frequency = Int()
    ModulationID = Int()
    Modulation = Reference(ModulationID, Modulation.ID)
    
    def __init__(self):
        self.Frequency = 0
        self.ModulationID = 0
    
    @staticmethod
    def importFromDom(store, node, broadcast, context):
        frequency = int(XMLIntf.getText(node))
        modname = node.getAttribute("modulation")
        checklist = store.find(BroadcastFrequency, 
            (BroadcastFrequency.Frequency == frequency) and
            (BroadcastFrequency.BroadcastID == broadcast.ID))
        for broadcastFrequency in checklist:
            if broadcastFrequency.Modulation.Name == modname:
                return broadcastFrequency
        
        obj = BroadcastFrequency()
        store.add(obj)
        obj.Broadcast = broadcast
        obj.fromDom(node, context)
        return obj
    
    def fromDom(self, node, context):
        self.Frequency = int(XMLIntf.getText(node))
        self.Modulation = Store.of(self).find(Modulation, Modulation.Name == node.getAttribute("modulation")).any()
        if self.Modulation is None:
            self.Modulation = Modulation()
            Store.of(self).add(self.Modulation)
            self.Modulation.Name = node.getAttribute("modulation")
    
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        frequency = XMLIntf.buildTextElementNS(doc, "frequency", unicode(self.Frequency), XMLIntf.namespace)
        frequency.setAttribute("modulation", self.Modulation.Name)
        parentNode.appendChild(frequency)
        

class Broadcast(PriyomBase, XMLIntf.XMLStorm):
    __storm_table__ = "broadcasts"
    ID = Int(primary = True)
    TransmissionDeleted = Int()
    StationID = Int()
    Type = Enum(map={
        "data": "data",
        "continous": "continous"
    })
    BroadcastStart = Int()
    BroadcastEnd = Int()
    ScheduleLeafID = Int()
    Confirmed = Bool()
    Comment = Unicode()
    Frequencies = ReferenceSet(ID, BroadcastFrequency.BroadcastID)
    
    xmlMapping = {
        u"Comment": "Comment",
        u"Type": "Type"
    }
    
    def __init__(self):
        super(Broadcast, self).__init__()
        self.Confirmed = False
        self.BroadcastStart = 0
        self.BroadcastEnd = None
        self.Comment = None
        self.StationID = 0
        
    def _dummy(self, element):
        pass
        
    def _loadStart(self, element, context):
        time = long(element.getAttribute("unix"))
        self.BroadcastStart = time
        
    def _loadEnd(self, element, context):
        time = long(element.getAttribute("unix"))
        self.BroadcastEnd = time
        
    def _loadConfirmed(self, element, context):
        if element.hasAttribute("delete"):
            self.Confirmed = False
        else:
            self.Confirmed = True
    
    def _loadFrequency(self, element, context):
        broadcastFrequency = BroadcastFrequency.importFromDom(Store.of(self), element, self, context)
        if element.hasAttribute("delete"):
            Store.of(self).remove(broadcastFrequency)
            
    def _loadStationID(self, node, context):
        self.StationID = context.resolveId(Station, int(XMLIntf.getText(node)))
    
    def getIsOnAir(self):
        now = datetime.datetime.utcnow()
        start = datetime.datetime.fromtimestamp(self.BroadcastStart)
        if now > start:
            if self.BroadcastEnd is None:
                return True
            else:
                end = datetime.datetime.fromtimestamp(self.BroadcastEnd)
                return now < end
        else:
            return False
        
    
    def toDom(self, parentNode, flags=None):
        doc = parentNode.ownerDocument
        broadcast = doc.createElementNS(XMLIntf.namespace, "broadcast")
        
        XMLIntf.appendTextElement(broadcast, "ID", unicode(self.ID))
        XMLIntf.appendDateElement(broadcast, "Start", self.BroadcastStart)
        if self.BroadcastEnd is not None:
            XMLIntf.appendDateElement(broadcast, "End", self.BroadcastEnd)
        XMLIntf.appendTextElements(broadcast,
            [
                ("StationID", unicode(self.StationID)),
                ("Type", self.Type),
                ("Confirmed", "" if self.Confirmed else None),
                ("on-air", "" if self.getIsOnAir() else None),
                ("has-transmissions", "" if self.Transmissions.count() > 0 else None)
            ]
        )
        for frequency in self.Frequencies:
            frequency.toDom(broadcast)
            
        if flags is not None and "broadcast-transmissions" in flags:
            for transmission in self.Transmissions:
                transmission.toDom(broadcast, flags)
        
        parentNode.appendChild(broadcast)
        
    def loadDomElement(self, node, context):
        print("loading %s" % node.tagName)
        try:
            {
                u"Start": self._loadStart,
                u"End": self._loadEnd,
                u"Confirmed": self._loadConfirmed,
                u"on-air": self._dummy,
                u"has-transmissions": self._dummy,
                u"frequency": self._loadFrequency
            }[node.tagName](node, context)
        except KeyError:
            pass
        
    def __str__(self):
        return "%s broadcast from %s until %s" % (self.Type, repr(self.BroadcastStart), repr(self.BroadcastEnd))
        
    def transmissionDeleted(self):
        self.TransmissionDeleted = now()
