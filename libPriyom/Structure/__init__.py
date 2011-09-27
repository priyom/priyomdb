from storm.schema.schema import Schema
import Patches

libPriyomSchema = Schema(
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

"""CREATE TABLE `transmissionClassTables` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `TransmissionClassID` INT NOT NULL COMMENT 'references transmissionClasses entry',
    `TableName` VARCHAR(255) NOT NULL COMMENT 'name of table to use',
    `DisplayName` VARCHAR(255) NOT NULL COMMENT 'display name for backend use',
    `XMLGroupClass` VARCHAR(255) NOT NULL COMMENT 'class attribute contents for xml output',
    PRIMARY KEY (`ID`),
    KEY `TransmissionClassID` (`TransmissionClassID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;""",

"""CREATE TABLE `transmissionClassTableFields` (
    `ID` INT NOT NULL AUTO_INCREMENT,
    `TransmissionClassTableID` INT NOT NULL COMMENT 'references transmissionClassTables entry',
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
) ENGINE=MyISAM  DEFAULT CHARSET=utf8;"""
    ],
    [
"""DROP TABLE `transmissions`;""",
"""DROP TABLE `transmissionClassTableFields`;""",
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
"""DROP TABLE `variables`;"""
    ],
    [
"""DELETE FROM `transmissions`;""",
"""DELETE FROM `transmissionClassTableFields`;""",
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
"""DELETE FROM `variables`;"""
    ],
    Patches
)
