from ..broadcasts import Broadcast
from ..schedules import Schedule
from ..stations import Station
from time import mktime
from datetime import datetime, timedelta

class ScheduleLeafDescription(object):
    def __init__(self, scheduleLeaf, timeAtStartOffset):
        self.leaf = scheduleLeaf
        self.offsetFromAlignment = timeAtStartOffset

class ScheduleMaintainer(object):
    def __init__(self, store):
        self.store = store
        
    @staticmethod
    def now():
        return int(mktime(datetime.utcnow().timetuple()))
        
    @staticmethod
    def toTimestamp(datetime):
        return int(mktime(datetime.timetuple()))
        
    @staticmethod
    def incMonth(dt, by):
        month = dt.month + by
        year = dt.year + int((month-1) / 12)
        month -= int((month-1) / 12) * 12
        return datetime(year=year, month=month, day=1)
        
    def findScheduleLeafRecurse(self, schedule, lowerConstraint, upperConstraint, timeAtStartOffset, time, allowClosest = False):
        for child in schedule.Children:
            match = self.findScheduleLeaf(schedule, lowerConstraint, upperConstraint, time, allowClosest)
            if match is not None:
                return match
        return ScheduleLeafDescription(schedule, timeAtStartOffset)
        
    def findScheduleLeafRecurseEx(self, schedule, lowerConstraint, upperConstraint, lcDate, ucDate, time, allowClosest = False):
        lc = ScheduleMaintainer.toTimestamp(lcDate) + schedule.StartTimeOffset
        if schedule.EndTimeOffset is not None:
            uc = ScheduleMaintainer.toTimestamp(lcDate) + schedule.EndTimeOffset
        else:
            uc = ScheduleMaintainer.toTimestamp(ucDate)
        if upperConstraint is not None:
            if uc > upperConstraint:
                uc = upperConstraint
        
        if (lc <= time) and (uc > time):
            origLc = lc
            if lowerConstraint is not None:
                if lc < lowerConstraint:
                    lc = lowerConstraint
            return self.findScheduleLeafRecurse(schedule, lc, uc, origLc, time, allowClosest)
        elif allowClosest and (lc > time):
            origLc = lc
            if lowerConstraint is not None:
                if lc < lowerConstraint:
                    lc = lowerConstraint
            return self.findScheduleLeafRecurse(schedule, lc, uc, origLc, lc, allowClosest)
        else:
            return None
        
    def findScheduleLeaf_once(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        lc = schedule.StartTimeOffset
        if lowerConstraint is not None:
            lc += lowerConstraint
        uc = schedule.EndTimeOffset
        if upperConstraint is not None:
            if uc is None:
                uc = upperConstraint
            else:
                uc += upperConstraint
        
        if lc <= time and (uc is None or uc > time):
            return self.findScheduleLeafRecurse(schedule, lc, uc, schedule.StartTimeOffset, time, allowClosest)
        elif allowClosest and lc > time:
            return self.findScheduleLeafRecurse(schedule, lc, uc, schedule.StartTimeOffset, lc, allowClosest)
        else:
            return None
            
    def findScheduleLeaf_year(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        lcDate = datetime.utcfromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year + schedule.Skip, day=1, month=1)
        ucDate = datetime(year=lcDate.year + 1, day=1, month=1)
        if schedule.Every is not None:
            while (uc <= time):
                if uc > upperConstraint:
                    return None
                lcDate = datetime(year=lcDate.year + schedule.Every)
                ucDate = datetime(year=lcDate.year + 1, day=1, month=1)
                uc = ScheduleMaintainer.toTimestamp(ucDate)
        
        return self.findScheduleLeafRecurseEx(schedule, lowerConstraint, upperConstraint, lcDate, ucDate, time, allowClosest)
            
    def findScheduleLeaf_month(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        lcDate = datetime.utcfromtimestamp(lowerConstraint)
        ScheduleMaintainer.incMonth(lcDate, schedule.Skip)
        lcDate = datetime(year=lcDate.year, month=startMonth, day=1)
        ucDate = ScheduleMaintainer.nextMonth(lcDate)
        if schedule.Every is not None:
            while (ScheduleMaintainer.toTimestamp(ucDate) <= time):
                startMonth = lcDate.month + schedule.Every
                if startMonth > 12:
                    return None
                lcDate = datetime(year=lcDate.year, month=startMonth, day=1)
                ucDate = ScheduleMaintainer.nextMonth(lcDate)
        
        return self.findScheduleLeafRecurseEx(schedule, lowerConstraint, upperConstraint, lcDate, ucDate, time, allowClosest)
    
    def findScheduleLeaf_week(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        lcDate = datetime.utcfromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year, month=lcDate.month, day=lcDate.day) # align to day boundaries
        interval = timedelta(days=7)
        lcDate = lcDate + interval * schedule.Skip
        ucDate = lcDate + interval
        if schedule.Every is not None:
            while (ScheduleMaintainer.toTimestamp(ucDate) <= time):
                lcDate += interval * schedule.Every
                ucDate = lcDate * interval
        
        return self.findScheduleLeafRecurseEx(schedule, lowerConstraint, upperConstraint, lcDate, ucDate, time, allowClosest)
        
    def findScheduleLeaf_day(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        lcDate = datetime.utcfromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year, month=lcDate.month, day=lcDate.day) # align to day boundaries
        interval = timedelta(days=1)
        
        lcDate = lcDate + interval * schedule.Skip
        ucDate = lcDate + interval
        if schedule.Every is not None:
            while (ScheduleMaintainer.toTimestamp(ucDate) <= time):
                lcDate += interval * schedule.Every
                ucDate = lcDate * interval
        
        return self.findScheduleLeafRecurseEx(schedule, lowerConstraint, upperConstraint, lcDate, ucDate, time, allowClosest)
        
    def findScheduleLeaf_hour(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        lcDate = datetime.utcfromtimestamp(lowerConstraint)
        lcDate = datetime(year=lcDate.year, month=lcDate.month, day=lcDate.day, hour=lcDate.hour) # align to hour boundaries
        interval = timedelta(hours=1)
        
        lcDate = lcDate + interval * schedule.Skip
        ucDate = lcDate + interval
        if schedule.Every is not None:
            while (ScheduleMaintainer.toTimestamp(ucDate) <= time):
                lcDate += interval * schedule.Every
                ucDate = lcDate * interval
        
        return self.findScheduleLeafRecurseEx(schedule, lowerConstraint, upperConstraint, lcDate, ucDate, time, allowClosest)
        
    def findScheduleLeaf(self, schedule, lowerConstraint, upperConstraint, time, allowClosest = False):
        method = getattr(self, "findScheduleLeaf_%s" % schedule.Kind)
        return method(schedule, lowerConstraint, upperConstraint, time, allowClosest)
        
    def findScheduleLeafAtTimeFromRoot(self, schedule, time, allowClosest = False):
        self.findScheduleLeaf(schedule, None, None, time, allowClosest)
        
    def getNextScheduleLeaf(self, leafDescription):
        return self.findScheduleLeaf(leafDescription.schedule, None, None, (leafDescription.timeAtStartOffset - schedule.StartTimeOffset) + schedule.EndTimeOffset, True)
    
    def updateSchedule(self, station, until):
        if station.Schedule is None:
            return
        if station.ScheduleUpToDateUntil is not None and station.ScheduleUpToDateUntil >= until:
            return
        if station.ScheduleUpToDateUntil is None:
            currLeaf = self.findNextScheduleLeaf(ScheduleMaintainer.now())
        else:
            currLeaf = self.findNextScheduleLeaf(station.ScheduleUpToDateUntil)
        
