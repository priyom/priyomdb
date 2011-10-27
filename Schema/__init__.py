"""
File name: __init__.py
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
from storm.schema.schema import Schema
import Patches

DatabaseSchema = Schema(
    [
"""CREATE TABLE `variables` (
    `Name` VARCHAR(255) NOT NULL,
    `Value` VARCHAR(255) DEFAULT NULL,
    PRIMARY KEY (`Name`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `foreignSupplement` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `LocalID` INT NOT NULL COMMENT 'ID of entry in target table',
    `FieldName` VARCHAR(255) NOT NULL COMMENT 'field name whose contents should be overwritten',
    `ForeignText` VARCHAR(255) NOT NULL COMMENT 'new contents',
    `LangCode` CHAR(5) NOT NULL COMMENT 'language code of new contents (must not be ''en'')',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `LocalID` (`LocalID`,`FieldName`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `modulations` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `schedules` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Created` BIGINT NOT NULL COMMENT 'creation of a row',
    `Modified` BIGINT NOT NULL COMMENT 'last modification of a row',
    `ParentID` INT DEFAULT NULL COMMENT 'may reference parent schedules entry',
    `Name` VARCHAR(255) NOT NULL COMMENT 'display name for backend',
    `ScheduleKind` ENUM('once','hour','day','week','month','year') NOT NULL COMMENT 'must be once for ParentID=NULL, anything else otherwise',
    `Skip` INT NOT NULL DEFAULT '0' COMMENT 'how many periods to skip before first instance',
    `Every` INT NOT NULL COMMENT 'repeat rate',
    `StartTimeOffset` INT NOT NULL COMMENT 'offset of leafs/childrens start relative to periods start',
    `EndTimeOffset` INT DEFAULT NULL COMMENT 'offset of leafs/childrens end',
    PRIMARY KEY (`ID`),
    KEY `Modified` (`Modified`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `stations` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Created` BIGINT NOT NULL COMMENT 'creation date of a row',
    `Modified` BIGINT NOT NULL COMMENT 'last modification date of a row',
    `BroadcastRemoved` BIGINT DEFAULT NULL COMMENT 'last removal of an associated broadcast',
    `EnigmaIdentifier` VARCHAR(16) NOT NULL COMMENT 'one of the well known enigma identifiers',
    `PriyomIdentifier` VARCHAR(63) DEFAULT NULL COMMENT 'priyom identifier of stations not identified by e2k',
    `Nickname` VARCHAR(255) DEFAULT NULL COMMENT 'a community-given nickname',
    `Description` TEXT NOT NULL COMMENT 'longer description, may contain basic html',
    `Status` VARCHAR(255) NOT NULL COMMENT 'status information',
    `Location` VARCHAR(255) DEFAULT NULL COMMENT 'location information; null if unknown',
    `ScheduleID` INT DEFAULT NULL COMMENT 'schedule; null if unknown/unset',
    `ScheduleConfirmed` BOOL NOT NULL DEFAULT '0' COMMENT 'whether the (not) assigned schedule is confirmed',
    `ScheduleUpToDateUntil` BIGINT DEFAULT NULL COMMENT 'state of the schedule instantiation',
    PRIMARY KEY (`ID`),
    KEY `BroadcastRemoved` (`BroadcastRemoved`),
    KEY `Modified` (`Modified`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `scheduleLeaves` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `StationID` INT NOT NULL COMMENT 'references stations entry',
    `ScheduleID` INT NOT NULL COMMENT 'references schedules entry',
    `BroadcastType` ENUM('continous','data') NOT NULL COMMENT 'type of the broadcast which is to be created',
    PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='n-to-m-to-k between schedules, frequencies and stations';""",

"""CREATE TABLE `scheduleLeafFrequencies` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `ScheduleLeafID` INT NOT NULL COMMENT 'references the schedule leaf',
    `Frequency` INT NOT NULL COMMENT 'frequency in Hz',
    `ModulationID` INT NOT NULL COMMENT 'references the modulation',
    PRIMARY KEY (`ID`),
    KEY `ScheduleLeafID` (`ScheduleLeafID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `broadcasts` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Created` BIGINT NOT NULL COMMENT 'creation of a row',
    `Modified` BIGINT NOT NULL COMMENT 'last modification of a row',
    `TransmissionRemoved` BIGINT DEFAULT NULL COMMENT 'last removal of an associated transmission',
    `StationID` INT NOT NULL,
    `Type` ENUM('continous','data') NOT NULL COMMENT 'continous == channel marker, data == may contain transmissions',
    `BroadcastStart` BIGINT NOT NULL,
    `BroadcastEnd` BIGINT DEFAULT NULL COMMENT 'if null, broadcast is still ongoing and end is unknown',
    `ScheduleLeafID` INT DEFAULT NULL,
    `Confirmed` BOOL NOT NULL COMMENT 'whether broadcast is confirmed',
    `Comment` VARCHAR(1023) DEFAULT NULL,
    PRIMARY KEY (`ID`),
    KEY `StationID` (`StationID`),
    KEY `Modified` (`Modified`),
    KEY `TransmissionRemoved` (`TransmissionRemoved`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `broadcastFrequencies` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `BroadcastID` INT NOT NULL COMMENT 'references broadcasts entry',
    `Frequency` INT NOT NULL COMMENT 'broadcast frequency in Hz',
    `ModulationID` INT NOT NULL COMMENT 'reference to modulations entry',
    PRIMARY KEY (`ID`),
    KEY `BroadcastID` (`BroadcastID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='assigns frequencies and modulations to broadcasts';""",

"""CREATE TABLE `transmissionParserNode` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `ParentID` INT DEFAULT NULL,
    `ParentGroup` INT DEFAULT NULL,
    `RegularExpression` VARCHAR(1024) NOT NULL,
    `TableID` INT DEFAULT NULL,
    PRIMARY KEY (`ID`),
    KEY `ParentID` (`ParentID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `transmissionParserNodeField` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `ParserNodeID` INT NOT NULL,
    `Group` INT NOT NULL,
    `ForeignGroup` INT DEFAULT NULL,
    `ForeignLangGroup` INT DEFAULT NULL,
    `FieldName` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`ID`),
    KEY `ParserNodeID` (`ParserNodeID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `transmissionClasses` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Created` BIGINT NOT NULL COMMENT 'creation of a row',
    `Modified` BIGINT NOT NULL COMMENT 'last modification of a row',
    `DisplayName` VARCHAR(255) NOT NULL COMMENT 'display name for backend use',
    `RootParserNodeID` INT DEFAULT NULL,
    PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `transmissionTables` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `TableName` VARCHAR(255) NOT NULL COMMENT 'name of table to use',
    `DisplayName` VARCHAR(255) NOT NULL COMMENT 'display name for backend use',
    `XMLGroupClass` VARCHAR(255) NOT NULL COMMENT 'class attribute contents for xml output',
    PRIMARY KEY (`ID`),
    KEY `TransmissionClassID` (`TransmissionClassID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `transmissionClassTables` (
    `ClassID` INT NOT NULL,
    `TableID` INT NOT NULL,
    PRIMARY KEY (`ClassID`, `TableID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;"""

"""CREATE TABLE `transmissionTableFields` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `TransmissionTableID` INT NOT NULL COMMENT 'references transmissionTables entry',
    `FieldNumber` INT NOT NULL COMMENT 'index of the field, not counting the first three fields, starting at 0',
    `FieldName` VARCHAR(255) NOT NULL,
    `Kind` ENUM('number','codeword','plaintext','other') NOT NULL DEFAULT 'other' COMMENT 'for xml output mostly, kind of fields contents',
    `MaxLength` INT NOT NULL COMMENT 'max length recommendation',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `TableField` (`TransmissionClassTableID`,`FieldNumber`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `transmissions` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Created` BIGINT NOT NULL COMMENT 'creation of a row',
    `Modified` BIGINT NOT NULL COMMENT 'last modification of a row',
    `BroadcastID` INT NOT NULL COMMENT 'may reference broadcast if known',
    `Callsign` VARCHAR(255) NOT NULL COMMENT 'callsign used for transmission',
    `Timestamp` INT NOT NULL COMMENT 'approximate timestamp of tx',
    `ClassID` INT NOT NULL COMMENT 'references transmissionClasses entry',
    `RecordingURL` VARCHAR(1023) DEFAULT NULL COMMENT 'may contain url to recording',
    `Remarks` VARCHAR(1023) DEFAULT NULL COMMENT 'may contain further remarks (reception etc)',
    PRIMARY KEY (`ID`),
    KEY `Modified` (`Modified`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `eventClass` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Title` VARCHAR(255) NOT NULL COMMENT 'title of the event class',
    `eventClasses` ADD `StateChanging` BOOL NOT NULL DEFAULT '0' COMMENT 'defines whether events in this class are so called state-changing events',
    PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8""",

"""CREATE TABLE `events` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Created` BIGINT NOT NULL COMMENT 'creation date of row',
    `Modified` BIGINT NOT NULL COMMENT 'last modification date of row',
    `StationID` INT NOT NULL COMMENT 'station to which the ID is associated',
    `EventClassID` INT DEFAULT NULL COMMENT 'event class, NULL for raw event',
    `Description` TEXT NOT NULL COMMENT 'descriptive text of the event',
    `StartTime` BIGINT NOT NULL COMMENT 'start time of the event, or time singularity of the event if EndTime is NULL',
    `EndTime` BIGINT DEFAULT NULL COMMENT 'end time of the event or NULL if its a singularity',
    PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8""",

"""CREATE TABLE `api-capabilities` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Capability` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`ID`),
    UNIQUE KEY `Capability` (`Capability`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `api-keys` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Key` VARCHAR(256) NOT NULL COMMENT 'api key',
    `CIDRList` VARCHAR(1024) DEFAULT NULL COMMENT 'valid ip ranges from which requests may be issued with this API key',
    PRIMARY KEY (`ID`),
    UNIQUE KEY `Key` (`Key`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='API keys for usage by priyomhttpd';""",

"""CREATE TABLE `api-keyCapabilities` (
    `KeyID` INT NOT NULL,
    `CapabilityID` INT NOT NULL,
    PRIMARY KEY (`KeyID`,`CapabilityID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `api-users` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `UserName` VARCHAR(255) NOT NULL,
    `EMail` VARCHAR(255) NOT NULL,
    `PasswordHash` CHAR(64) NOT NULL,
    `PasswordSalt` CHAR(32) NOT NULL,
    PRIMARY KEY (`ID`),
    UNIQUE KEY `UserName` (`UserName`),
    UNIQUE KEY `EMail` (`EMail`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `api-userCapabilities` (
    `UserID` INT NOT NULL,
    `CapabilityID` INT NOT NULL,
    PRIMARY KEY (`UserID`,`CapabilityID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `api-sessions` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Key` VARCHAR(256) NOT NULL,
    `UserID` INT NOT NULL,
    `Expires` BIGINT NOT NULL,
    PRIMARY KEY (`ID`),
    UNIQUE KEY `Key` (`Key`),
    UNIQUE KEY `UserID` (`UserID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `api-sessionCapabilities` (
    `SessionID` INT NOT NULL,
    `CapabilityID` INT NOT NULL,
    PRIMARY KEY (`SessionID`,`CapabilityID`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `api-news` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `Title` VARCHAR(256) NOT NULL,
    `Contents` TEXT NOT NULL,
    `Timestamp` BIGINT NOT NULL,
    PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;"""
    ],
    [
"""DROP TABLE `transmissions`;""",
"""DROP TABLE `transmissionTableFields`;""",
"""DROP TABLE `transmissionTables`;""",
"""DROP TABLE `transmissionClassTables`;""",
"""DROP TABLE `transmissionClasses`;""",
"""DROP TABLE `transmissionParserNodeField`;""",
"""DROP TABLE `transmissionParserNode`;""",
"""DROP TABLE `broadcastFrequencies`;""",
"""DROP TABLE `broadcasts`;""",
"""DROP TABLE `scheduleLeafFrequencies`;""",
"""DROP TABLE `scheduleLeaves`;""",
"""DROP TABLE `stations`;""",
"""DROP TABLE `schedules`;""",
"""DROP TABLE `modulations`;""",
"""DROP TABLE `foreignSupplement`;""",
"""DROP TABLE `variables`;""",
"""DROP TABLE `api-news`;""",
"""DROP TABLE `api-sessionCapabilities`;""",
"""DROP TABLE `api-userCapabilities`;""",
"""DROP TABLE `api-keyCapabilities`;""",
"""DROP TABLE `api-sessions`;""",
"""DROP TABLE `api-users`;""",
"""DROP TABLE `api-keys`;""",
"""DROP TABLE `api-capabilities`;"""
    ],
    [
"""DELETE FROM `transmissions`;""",
"""DELETE FROM `transmissionTables`;""",
"""DELETE FROM `transmissionTableFields`;""",
"""DELETE FROM `transmissionClassTables`;""",
"""DELETE FROM `transmissionClasses`;""",
"""DELETE FROM `transmissionParserNodeField`;""",
"""DELETE FROM `transmissionParserNode`;""",
"""DELETE FROM `broadcastFrequencies`;""",
"""DELETE FROM `broadcasts`;""",
"""DELETE FROM `scheduleLeafFrequencies`;""",
"""DELETE FROM `scheduleLeaves`;""",
"""DELETE FROM `stations`;""",
"""DELETE FROM `schedules`;""",
"""DELETE FROM `modulations`;""",
"""DELETE FROM `foreignSupplement`;""",
"""DELETE FROM `variables`;""",
"""DELETE FROM `api-news`;""",
"""DELETE FROM `api-sessionCapabilities`;""",
"""DELETE FROM `api-userCapabilities`;""",
"""DELETE FROM `api-keyCapabilities`;""",
"""DELETE FROM `api-sessions`;""",
"""DELETE FROM `api-users`;""",
"""DELETE FROM `api-keys`;""",
"""DELETE FROM `api-capabilities`;"""
    ],
    Patches
)
