#!/usr/bin/python3

"""
File name: s28csv-to-queries.py
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
stationId = 1
frequency = 4625000
modulationId = 3
classId = 1

monthname_to_idx = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12
}

import csv
import re
from time import mktime
from datetime import datetime
import sys

def mysqlEscape(str):
    return str.replace("\\", "\\\\").replace("\"", "\\\"")

pDayMonth = re.compile("([A-Z][a-z]{2})[a-z]*\s+([0-9]+)")
pTime = re.compile("([0-9X?]{1,2}):([0-9X?]{2})")
pData = re.compile("(([0-9X?]{2})\s+([0-9X?]{3})|([^ ]+)\s+([0-9X?]{2})\s+([0-9X?]{2})\s+([0-9X?]{2})\s+([0-9X?]{2}))")

skippedRows = []
reader = csv.reader(open('s28-2011.csv', newline=''))
for row in reader:
    if row[-1][-5:] == "#skip":
        skippedRows.append(row)
        continue
    if len(row) != 8:
        print("invalid row length: {0:d}\n{1}".format(len(row), repr(row)))
        break
    daymonth = row[0].lstrip().rstrip()
    year = row[1].lstrip().rstrip()
    time = row[2].lstrip().rstrip()
    callsign = row[3].lstrip().rstrip()
    recording = row[4].lstrip().rstrip()
    data = row[5].lstrip().rstrip()
    ru = row[6].lstrip().rstrip()
    comment = row[7].lstrip().rstrip()
    
    match = pDayMonth.match(daymonth)
    if match is None:
        print("Date parser failed on row:\n{0}".format(repr(row)))
        break
    matchGroups = match.groups()
    
    month = matchGroups[0]
    day = int(matchGroups[1])
    
    year = int(year)
    
    timeApproximate = False
    if len(time) > 0:
        match = pTime.match(time)
        if match is None:
            print("Time parser failed on row:\n{0}".format(repr(row)))
            break
        matchGroups = match.groups()
        
        try:
            hour = int(matchGroups[0])
        except ValueError:
            hour = 0
            timeApproximate = 3600
        
        try:
            minute = int(matchGroups[1])
        except ValueError:
            minute = 0
            timeApproximate = 60
    else:
        hour = 0
        minute = 0
        timeApproximate = 3600*24
        
    if timeApproximate != False:
        if timeApproximate == 60:
            addComment = "Time approximate (minute level)"
        elif timeApproximate == 3600:
            addComment = "Time approximate (hour level)"
        else:
            addComment = "Time approximate (only day is certain)"
        comment = comment + "; " + addComment if len(comment) > 2 else addComment
    
    (callsignLatin, dummy, callsignRu) = callsign.partition("/")
    
    dataMatches = list(pData.finditer(data))
    if len(dataMatches) == 0 and (len(data) != 0):
        print("Data parser failed on row:\n{0}".format(repr(row)))
        break
    
    ruReplacements = [s.lstrip().rstrip() for s in ru.split(";")]
        
    timestamp = int(mktime(datetime(year=year, month=monthname_to_idx[month], day=day, hour=hour, minute=minute).timetuple()))
    
    print("""
INSERT INTO `broadcasts` 
    (Created,          Modified,         StationID, Type,   BroadcastStart, BroadcastEnd, ScheduleLeafID, Confirmed) VALUES 
    (UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), {0:d},     "data", {1:d},          {2:d},        NULL,           1);
SELECT @broadcastId:=LAST_INSERT_ID();
INSERT INTO `broadcastFrequencies`
    (BroadcastID,   Frequency,  ModulationID) VALUES
    (@broadcastId,  {3:d},      {4:d});
INSERT INTO `transmissions`
    (Created,          Modified,         BroadcastID, Callsign, Timestamp, ClassID, RecordingURL, Remarks) VALUES
    (UNIX_TIMESTAMP(), UNIX_TIMESTAMP(), @broadcastId, "{5}",     {6:d},     {7:d}, {9},          {8});
SELECT @transmissionId:=LAST_INSERT_ID();""".format(
        stationId,
        timestamp - 60,
        timestamp + 2*len(dataMatches)*15 + 60,
        frequency,
        modulationId,
        mysqlEscape(callsignLatin),
        timestamp,
        classId,
        '"'+mysqlEscape(comment)+'"' if comment != '-' else "NULL",
        '"'+mysqlEscape("http://priyom.org"+recording)+'"' if len(recording) > 2 else "NULL"
        ), end="")
    if len(callsignRu) > 0:
        print("""
INSERT INTO `foreignSupplement` 
    (LocalID,           FieldName,                  ForeignText, LangCode) VALUES
    (@transmissionId,   'transmissions.Callsign',   "{0}",       "ru");""".format(
            mysqlEscape(callsignRu),
            ), end="")
    
    order = 0
    for match in dataMatches:
        groups = match.groups()
        if groups[1] is not None:
            # s28-leading
            print("""
INSERT INTO `s28-leading`
    (TransmissionID,    `Order`,    Number1,    Number2) VALUES
    (@transmissionID,   {0:d},      "{1}",      "{2}");""".format(
                order,
                mysqlEscape(groups[1]),
                mysqlEscape(groups[2])
                ), end="")
        elif groups[3] is not None:
            # s28-block
            print("""
INSERT INTO `s28-blocks`
    (TransmissionID,    `Order`,    Codeword,   Number1,    Number2,    Number3,    Number4) VALUES
    (@transmissionId,   {0:d},      "{1}",      "{2}",      "{3}",      "{4}",      "{5}");""".format(
                order,
                mysqlEscape(groups[3]),
                mysqlEscape(groups[4]),
                mysqlEscape(groups[5]),
                mysqlEscape(groups[6]),
                mysqlEscape(groups[7]),
                ), end="")
            if len(ruReplacements) > 0:
                print("""
INSERT INTO `foreignSupplement`
    (LocalID,           FieldName,               ForeignText,    LangCode) VALUES
    (LAST_INSERT_ID(),  "s28-blocks.Codeword",   "{0}",          "ru");""".format(
                    mysqlEscape(ruReplacements.pop(0))
                    ), end="")
        order += 1
    print()

print()
