import time
import datetime
from sortedcontainers import SortedList

class RequestItem:
    
    def __init__(self, code, timestamp):
        self._code = code
        self._timestamp = timestamp
        
    def __lt__(self, other):
        if type(other) == RequestItem:
            return self._timestamp < other._timestamp
        else:
            return self._timestamp < other
    
    def __eq__(self, other):
        return self._timestamp == other._timestamp
    
    def __repr__(self):
        return "{:.0f}:{}".format(self._timestamp, self._code)
        

class RequestLogger:
    
    def __init__(self):
        self._requests = []
        self._current_window = SortedList([])
        
    def push_request(self, url, code, r):
        if "Date" in r:
            r_data = RequestItem(code, time.mktime(datetime.datetime.strptime(r["Date"], "%a, %d %b %Y %H:%M:%S %Z").timetuple()))
        else:
            r_data = RequestItem(code, 0)
        self._requests.append(r_data)
        self._current_window.add(r_data)
        
    def get_window_stats(self):
        self._current_window = SortedList(self._current_window[self._current_window.bisect_left(time.time() - 60):])
        values = [r._code for r in self._current_window]
        return {x:values.count(x) for x in set(values)}
        
    def get_stats(self):
        values = [r._code for r in self._requests]
        return {x:values.count(x) for x in set(values)}
        