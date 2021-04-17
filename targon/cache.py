from sortedcontainers import SortedSet
import asyncio

class Cache:
    
    def __init__(self):
        self._container = SortedSet()
        self._lock = asyncio.Lock()
        
    def has(self, item):
        return item in self._container
    
    def add(self, item):
        self._container.add(item)
        
    async def add_and_check(self, item):
        with await self._lock:
            # Insert if it is not already in
            if not (is_in := self.has(item)):
                self._container.add(item)
            # Return if it was already in or not
            return is_in