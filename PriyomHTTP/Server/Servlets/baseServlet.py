import cStringIO
import time
import datetime
from ..errors import ServletError

class Servlet(object):
    weekdayname = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    monthname = [None, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    def __init__(self, instanceName, priyomInterface):
        self.instanceName = instanceName
        self.priyomInterface = priyomInterface
        self.store = self.priyomInterface.store
        self.allowPrefixes = False
        self.allowCommandPaths = False
        
    def _limitResults(self, resultSet, arguments):
        offset = None
        try:
            offset = int(arguments["offset"])
        except KeyError:
            pass
        except ValueError:
            pass
        limit = None
        try:
            limit = int(arguments["limit"])
        except KeyError:
            pass
        except ValueError:
            pass
        distinct = "distinct" in arguments and arguments["distinct"] == u"1"
        resultSet.config(distinct, offset, limit)
        return resultSet
        
    def formatDate(self, dt):
        return dt.strftime("%%s, %d %%s %Y %T UTC") % (Servlet.weekdayname[dt.weekday()], Servlet.monthname[dt.month])
        
    def formatTimestamp(self, timestamp):
        return self.formatDate(datetime.datetime.fromtimestamp(timestamp))
