"""
File name: patch_4.py
This file is part of: priyomdb

LICENSE

The contents of this file are subject to the Mozilla Public License
Version 1.1 (the "License"); you may not use this file except in
compliance with the License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/

Software distributed under the License is distributed on an "AS IS"
basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
License for the specific language governing rights and limitations under
the License.

Alternatively, the contents of this file may be used under the terms of
the GNU General Public license (the  "GPL License"), in which case  the
provisions of GPL License are applicable instead of those above.

FEEDBACK & QUESTIONS

For feedback and questions about priyomdb please e-mail one of the
authors:
    Jonas Wielicki <j.wielicki@sotecware.net>
"""

def apply(store):
    statements = [
"""RENAME TABLE `transmissionClassTables` TO `transmissionTables`""",
"""RENAME TABLE `transmissionClassTableFields` TO `transmissionTableFields`"""
"""CREATE TABLE `transmissionClassTables` (
    `ClassID` INT NOT NULL,
    `TableID` INT NOT NULL,
    PRIMARY KEY (`ClassID`, `TableID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8""",
"""INSERT INTO `transmissionClassTables` (`ClassID`, `TableID`) SELECT `TransmissionClassID`, `ID` FROM `transmissionTables`""",
"""ALTER TABLE `transmissionClassTables` DROP `TransmissionClassID`""",
"""ALTER TABLE `transmissionTableFields` CHANGE `TransmissionClassTableID` `TransmissionTableID` INT NOT NULL COMMENT 'references transmissionTables entry'"""
]
    for statement in statements:
        store.execute(statement)


