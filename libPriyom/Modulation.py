from storm.locals import *
import XMLIntf

class Modulation(object):
    __storm_table__ = "modulations"
    ID = Int(primary = True)
    Name = Unicode()

"""class Frequency(object):
    __storm_table__ = "frequencies"
    ID = Int(primary = True)
    Frequency = Int()
    ModulationID = Int()
    Modulation = Reference(ModulationID, Modulation.ID)
    
    def toDom(self, parentNode):
        doc = parentNode.ownerDocument
        frequency = XMLIntf.buildTextElementNS(doc, "frequency", unicode(self.Frequency), XMLIntf.namespace)
        frequency.setAttribute("modulation", self.Modulation.Name)
        parentNode.appendChild(frequency)

"""
