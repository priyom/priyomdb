"""
File name: Formatting.py
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
priyomdate = "%Y-%m-%dT%H:%M:%S"
import libPriyom.Helpers.TimeUtils as TimeUtils

class Formatters(object):
    @classmethod
    def catchNone(cls, othFormatter, noneValue=u"None"):
        def catch_none(value):
            if value is None:
                return noneValue
            else:
                return othFormatter(value)
        return catch_none
    
    @classmethod
    def Timestamp(cls):
        def timestamp(value):
            return TimeUtils.fromTimestamp(value).strftime(priyomdate)
        return timestamp
    
    @classmethod
    def Date(cls):
        def date(value):
            return value.strftime(priyomdate)
        return date
