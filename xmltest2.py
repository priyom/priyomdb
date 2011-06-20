#!/usr/bin/python2.7
from priyomdbtest import *
doc = dom.parse("test2.xml")
intf.importFromDom(doc.documentElement.getElementsByTagName("transmission")[0])
print(buzzer.PriyomIdentifier)
print(buzzer.Broadcasts.count())
