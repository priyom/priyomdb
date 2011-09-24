from datetime import datetime, timedelta
from calendar import timegm

def toTimestamp(datetime):
    return timegm(datetime.utctimetuple())
    
def toDatetime(timestamp):
    return datetime.utcfromtimestamp(timestamp)
    
def now():
    return toTimestamp(datetime.utcnow())

fromTimestamp = toDatetime
