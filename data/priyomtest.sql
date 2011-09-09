SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT=0;
START TRANSACTION;
SET time_zone = "+00:00";

DROP TABLE IF EXISTS `broadcastFrequencies`;
CREATE TABLE `broadcastFrequencies` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `BroadcastID` int(11) NOT NULL COMMENT 'references broadcasts entry',
  `Frequency` int(11) NOT NULL COMMENT 'broadcast frequency in Hz',
  `ModulationID` int(11) NOT NULL COMMENT 'reference to modulations entry',
  PRIMARY KEY (`ID`),
  KEY `BroadcastID` (`BroadcastID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='assigns frequencies and modulations to broadcasts' AUTO_INCREMENT=12 ;

INSERT INTO `broadcastFrequencies` (`ID`, `BroadcastID`, `Frequency`, `ModulationID`) VALUES
(1, 1, 4625000, 3),
(2, 5, 1377000, 1),
(3, 6, 1337000, 1),
(4, 1, 1337000, 1),
(5, 7, 4625000, 3),
(6, 7, 1337000, 4),
(9, 18, 1280000, 2),
(10, 244, 1234000, 1),
(11, 251, 4567000, 1);

DROP TABLE IF EXISTS `broadcasts`;
CREATE TABLE `broadcasts` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `StationID` int(11) NOT NULL,
  `Type` enum('continous','data') NOT NULL COMMENT 'continous == channel marker, data == may contain transmissions',
  `BroadcastStart` int(11) NOT NULL,
  `BroadcastEnd` int(11) DEFAULT NULL COMMENT 'if null, broadcast is still ongoing and end is unknown',
  `ScheduleLeafID` int(11) DEFAULT NULL,
  `Confirmed` tinyint(1) NOT NULL COMMENT 'whether broadcast is confirmed',
  `Comment` varchar(1023) DEFAULT NULL,
  PRIMARY KEY (`ID`),
  KEY `StationID` (`StationID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=252 ;

INSERT INTO `broadcasts` (`ID`, `StationID`, `Type`, `BroadcastStart`, `BroadcastEnd`, `ScheduleLeafID`, `Confirmed`, `Comment`) VALUES
(1, 1, 'continous', 533689200, NULL, NULL, 1, ''),
(7, 1, 'data', 1294232460, 1294232640, NULL, 1, ''),
(18, 1, 'continous', 0, NULL, NULL, 1, 'test'),
(251, 2, 'continous', 1309168800, 1309212000, 6, 0, NULL),
(250, 2, 'continous', 1309082400, 1309125600, 6, 0, NULL),
(249, 2, 'continous', 1308996000, 1309039200, 6, 0, NULL),
(248, 2, 'continous', 1308909600, 1308952800, 6, 0, NULL),
(247, 2, 'continous', 1308823200, 1308866400, 6, 0, NULL),
(246, 2, 'continous', 1308736800, 1308780000, 6, 0, NULL),
(245, 2, 'continous', 1308650400, 1308693600, 6, 0, NULL),
(244, 2, 'continous', 1309125600, 1309168800, 3, 0, NULL),
(243, 2, 'continous', 1309039200, 1309082400, 3, 0, NULL),
(242, 2, 'continous', 1308952800, 1308996000, 3, 0, NULL),
(241, 2, 'continous', 1308866400, 1308909600, 3, 0, NULL),
(240, 2, 'continous', 1308780000, 1308823200, 3, 0, NULL),
(239, 2, 'continous', 1308693600, 1308736800, 3, 0, NULL),
(238, 2, 'continous', 1308607200, 1308650400, 3, 0, NULL);

DROP TABLE IF EXISTS `foreignSupplement`;
CREATE TABLE `foreignSupplement` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `LocalID` int(11) NOT NULL COMMENT 'ID of entry in target table',
  `FieldName` varchar(255) NOT NULL COMMENT 'field name whose contents should be overwritten',
  `ForeignText` varchar(255) NOT NULL COMMENT 'new contents',
  `LangCode` char(5) NOT NULL COMMENT 'language code of new contents (must not be ''en'')',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `LocalID` (`LocalID`,`FieldName`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=11 ;

INSERT INTO `foreignSupplement` (`ID`, `LocalID`, `FieldName`, `ForeignText`, `LangCode`) VALUES
(1, 1, 'transmissions.Callsign', 'МДЖБ', 'ru'),
(2, 2, 'transmissions.Callsign', 'МДЖБ', 'ru'),
(3, 1, 's28-blocks.Codeword', 'СКОПЛЕНИЕ', 'ru'),
(4, 2, 's28-blocks.Codeword', 'ИКОНОМЕТР', 'ru'),
(5, 1, 's28-leading.Number1', '', ''),
(6, 1, 's28-leading.Number2', '', ''),
(7, 1, 's28-blocks.Number1', '', ''),
(8, 1, 's28-blocks.Number2', '', ''),
(9, 1, 's28-blocks.Number3', '', ''),
(10, 1, 's28-blocks.Number4', '', '');

DROP TABLE IF EXISTS `modulations`;
CREATE TABLE `modulations` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `Name` varchar(255) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6 ;

INSERT INTO `modulations` (`ID`, `Name`) VALUES
(1, 'AM'),
(2, 'LSB'),
(3, 'USB'),
(4, 'CW (morse)'),
(5, 'USB+RTTY');

DROP TABLE IF EXISTS `s28-blocks`;
CREATE TABLE `s28-blocks` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TransmissionID` int(11) NOT NULL,
  `Order` int(11) NOT NULL,
  `Codeword` varchar(255) NOT NULL,
  `Number1` char(2) NOT NULL,
  `Number2` char(2) NOT NULL,
  `Number3` char(2) NOT NULL,
  `Number4` char(2) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

INSERT INTO `s28-blocks` (`ID`, `TransmissionID`, `Order`, `Codeword`, `Number1`, `Number2`, `Number3`, `Number4`) VALUES
(1, 1, 1, 'SKOPLENIYe', '15', '81', '75', '54'),
(2, 2, 1, 'IKONOMETR', '65', '71', '18', '45');

DROP TABLE IF EXISTS `s28-leading`;
CREATE TABLE `s28-leading` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TransmissionID` int(11) NOT NULL,
  `Order` int(11) NOT NULL,
  `Number1` char(2) NOT NULL,
  `Number2` char(3) NOT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

INSERT INTO `s28-leading` (`ID`, `TransmissionID`, `Order`, `Number1`, `Number2`) VALUES
(1, 1, 0, '79', '612'),
(2, 2, 0, '26', '739');

DROP TABLE IF EXISTS `scheduleLeafFrequencies`;
CREATE TABLE `scheduleLeafFrequencies` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ScheduleLeafID` int(11) NOT NULL COMMENT 'references the schedule leaf',
  `Frequency` int(11) NOT NULL COMMENT 'frequency in Hz',
  `ModulationID` int(11) NOT NULL COMMENT 'references the modulation',
  PRIMARY KEY (`ID`),
  KEY `ScheduleLeafID` (`ScheduleLeafID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7 ;

INSERT INTO `scheduleLeafFrequencies` (`ID`, `ScheduleLeafID`, `Frequency`, `ModulationID`) VALUES
(1, 1, 1234000, 1),
(2, 2, 1234000, 1),
(3, 3, 1234000, 1),
(4, 4, 4567000, 1),
(5, 5, 4567000, 1),
(6, 6, 4567000, 1);

DROP TABLE IF EXISTS `scheduleLeaves`;
CREATE TABLE `scheduleLeaves` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `StationID` int(11) NOT NULL COMMENT 'references stations entry',
  `ScheduleID` int(11) NOT NULL COMMENT 'references schedules entry',
  `BroadcastType` enum('continous','data') NOT NULL COMMENT 'type of the broadcast which is to be created',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='n-to-m-to-k between schedules, frequencies and stations' AUTO_INCREMENT=7 ;

INSERT INTO `scheduleLeaves` (`ID`, `StationID`, `ScheduleID`, `BroadcastType`) VALUES
(1, 2, 9, 'continous'),
(2, 2, 10, 'continous'),
(3, 2, 13, 'continous'),
(4, 2, 11, 'continous'),
(5, 2, 12, 'continous'),
(6, 2, 14, 'continous');

DROP TABLE IF EXISTS `schedules`;
CREATE TABLE `schedules` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `ParentID` int(11) DEFAULT NULL COMMENT 'may reference parent schedules entry',
  `Name` varchar(255) NOT NULL COMMENT 'display name for backend',
  `ScheduleKind` enum('once','hour','day','week','month','year') NOT NULL COMMENT 'must be once for ParentID=NULL, anything else otherwise',
  `Skip` int(11) NOT NULL DEFAULT '0' COMMENT 'how many periods to skip before first instance',
  `Every` int(11) NOT NULL COMMENT 'repeat rate',
  `StartTimeOffset` int(11) NOT NULL COMMENT 'offset of leafs/childrens start relative to periods start',
  `EndTimeOffset` int(11) DEFAULT NULL COMMENT 'offset of leafs/childrens end',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=15 ;

INSERT INTO `schedules` (`ID`, `ParentID`, `Name`, `ScheduleKind`, `Skip`, `Every`, `StartTimeOffset`, `EndTimeOffset`) VALUES
(7, 5, 'pip schedule/summer', 'year', 0, 1, 7776000, 23759999),
(6, 5, 'pip schedule/winter part 1', 'year', 0, 1, 0, 7775999),
(5, NULL, 'pip schedule', 'once', 0, 0, 1293836400, NULL),
(8, 5, 'pip schedule/winter part 2', 'year', 0, 1, 23760000, 31535999),
(9, 6, 'pip schedule/winter part 1/morning', 'day', 0, 1, 0, 46800),
(10, 8, 'pip schedule/winter part 2/morning', 'day', 0, 1, 0, 46800),
(11, 6, 'pip schedule/winter part 1/afternoon', 'day', 0, 1, 46800, 86400),
(12, 8, 'pip schedule/winter part 2/afternoon', 'day', 0, 1, 46800, 86400),
(13, 7, 'pip schedule/summer/morning', 'day', 0, 1, 0, 43200),
(14, 7, 'pip schedule/summer/afternoon', 'day', 0, 1, 43200, 86400);

DROP TABLE IF EXISTS `stations`;
CREATE TABLE `stations` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `EnigmaIdentifier` varchar(16) NOT NULL COMMENT 'one of the well known enigma ids',
  `PriyomIdentifier` varchar(63) DEFAULT NULL COMMENT 'priyom identifier for stations which are not defined by e2k',
  `Nickname` varchar(255) NOT NULL COMMENT 'a community-given nickname',
  `Description` text NOT NULL COMMENT 'longer description, may contain basic html',
  `Status` varchar(255) NOT NULL COMMENT 'status information',
  `Location` varchar(255) DEFAULT NULL COMMENT 'location information; null if unknown',
  `ScheduleID` int(11) DEFAULT NULL COMMENT 'schedule; null if unknown/unset',
  `ScheduleConfirmed` tinyint(1) NOT NULL DEFAULT '0' COMMENT 'whether the (not) assigned schedule is confirmed',
  `ScheduleUpToDateUntil` bigint(20) DEFAULT NULL COMMENT 'state of the schedule instantiation',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

INSERT INTO `stations` (`ID`, `EnigmaIdentifier`, `PriyomIdentifier`, `Nickname`, `Description`, `Status`, `Location`, `ScheduleID`, `ScheduleConfirmed`, `ScheduleUpToDateUntil`) VALUES
(1, 'S28', 'B10', 'Buzzer', 'buzz, buzz, buzz', 'Actively buzzing.', 'Not sure anymore', NULL, 1, NULL),
(2, 'h0F', NULL, 'Fictional', 'Just for testing schedules and stuff.', 'Goes round and round and round…', 'Right behind you.', 5, 0, 1309200060);

DROP TABLE IF EXISTS `transmissionClasses`;
CREATE TABLE `transmissionClasses` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `DisplayName` varchar(255) NOT NULL COMMENT 'display name for backend use',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

INSERT INTO `transmissionClasses` (`ID`, `DisplayName`) VALUES
(1, 'S28 default');

DROP TABLE IF EXISTS `transmissionClassTableFields`;
CREATE TABLE `transmissionClassTableFields` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TransmissionClassTableID` int(11) NOT NULL COMMENT 'references transmissionClassTables entry',
  `FieldNumber` int(11) NOT NULL COMMENT 'index of the field, not counting the first three fields, starting at 0',
  `FieldName` varchar(255) NOT NULL,
  `Kind` enum('number','codeword','plaintext','other') NOT NULL DEFAULT 'other' COMMENT 'for xml output mostly, kind of fields contents',
  `MaxLength` int(11) NOT NULL COMMENT 'max length recommendation',
  PRIMARY KEY (`ID`),
  UNIQUE KEY `TableField` (`TransmissionClassTableID`,`FieldNumber`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=8 ;

INSERT INTO `transmissionClassTableFields` (`ID`, `TransmissionClassTableID`, `FieldNumber`, `FieldName`, `Kind`, `MaxLength`) VALUES
(1, 1, 0, 'Number1', 'number', 2),
(2, 1, 1, 'Number2', 'number', 3),
(3, 2, 0, 'Codeword', 'codeword', 0),
(4, 2, 1, 'Number1', 'number', 2),
(5, 2, 2, 'Number2', 'number', 2),
(6, 2, 3, 'Number3', 'number', 2),
(7, 2, 4, 'Number4', 'number', 2);

DROP TABLE IF EXISTS `transmissionClassTables`;
CREATE TABLE `transmissionClassTables` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `TransmissionClassID` int(11) NOT NULL COMMENT 'references transmissionClasses entry',
  `TableName` varchar(255) NOT NULL COMMENT 'name of table to use',
  `DisplayName` varchar(255) NOT NULL COMMENT 'display name for backend use',
  `XMLGroupClass` varchar(255) NOT NULL COMMENT 'class attribute contents for xml output',
  PRIMARY KEY (`ID`),
  KEY `TransmissionClassID` (`TransmissionClassID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

INSERT INTO `transmissionClassTables` (`ID`, `TransmissionClassID`, `TableName`, `DisplayName`, `XMLGroupClass`) VALUES
(1, 1, 's28-leading', 'S28-style addressee', 'id'),
(2, 1, 's28-blocks', 'S28-style code blocks', 'data');

DROP TABLE IF EXISTS `transmissions`;
CREATE TABLE `transmissions` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `StationID` int(11) NOT NULL COMMENT 'must reference broadcasting station',
  `BroadcastID` int(11) NOT NULL COMMENT 'may reference broadcast if known',
  `Callsign` varchar(255) NOT NULL COMMENT 'callsign used for transmission',
  `Timestamp` int(11) NOT NULL COMMENT 'approximate timestamp of tx',
  `ClassID` int(11) NOT NULL COMMENT 'references transmissionClasses entry',
  `RecordingURL` varchar(1023) DEFAULT NULL COMMENT 'may contain url to recording',
  `Remarks` varchar(1023) DEFAULT NULL COMMENT 'may contain further remarks (reception etc)',
  PRIMARY KEY (`ID`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=3 ;

INSERT INTO `transmissions` (`ID`, `StationID`, `BroadcastID`, `Callsign`, `Timestamp`, `ClassID`, `RecordingURL`, `Remarks`) VALUES
(1, 1, 7, 'MDZhB', 1294232520, 1, 'http://null.fstab.net/', 'weird'),
(2, 1, 7, 'MDZhB', 1294232580, 1, NULL, NULL);
COMMIT;
