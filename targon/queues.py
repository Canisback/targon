import asyncio
from .cache import Cache


class Queue():
    n = 0
    
    def __init__(self, name=None):
        self._queue = asyncio.Queue()
        
        self.set_name(name)
            
    def set_name(self, name=None):
        if name is None:
            self.name = "Queue" + str(Queue.n)
            Queue.n += 1
        else:
            self.name = name
        
        
    async def put(self, item):
        await self._queue.put(item)
        
    def put_nowait(self, item):
        self._queue.put_nowait(item)
        
    async def get(self):
        return await self._queue.get()
    
    def empty(self):
        return self._queue.empty()
    
    def __str__(self):
        return "{} : {} elements".format(self.name, len(self._queue._queue))
    
    
class CachedInQueue(Queue):
    # Do not let the same value in twice
    
    def __init__(self, cache=None, name=None):
        
        super().__init__(name)
        
        if cache is None:
            self._cache = Cache()
        else:
            self._cache = cache
        
    async def put(self, item):
        if item is None:
            return
        # Put in the queue only if the item is not in the cache
        if not (await self._cache.add_and_check(item)):
            await self._queue.put(item)
    
class CachedOutQueue(Queue):
    # Do not let the same value out twice
    
    def __init__(self, cache=None, name=None):
        
        super().__init__(name)
        
        if cache is None:
            self._cache = Cache()
        else:
            self._cache = cache
        
    async def get(self):
        while self._cache.add_and_check(item := await self._queue.get()) :
            pass
        await self._queue.get(item)
    