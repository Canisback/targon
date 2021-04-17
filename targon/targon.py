from .callers.callers import Manager
from .queues import Queue
from .loggers import RequestLogger
from .bootstrap import Bootstrap

import asyncio
import time

from pantheon import pantheon

try:
    import nest_asyncio
    nest_asyncio.apply()
except:
    pass


class Targon:
    
    def __init__(self, elements, server=None, api_key=None):
        self._managers = []
        self._queues = []
        self._bootstrap = []
        self._logger = RequestLogger()
        
        self._elements = elements
        
        self._server = server
        self._api_key = api_key
                
        self._running = False
        self._init = False
        
    def set_api_key(self, api_key):
        self._api_key = api_key
        
    def set_server(self, server):
        self._server = server
            
    
    def init_elements(self):
        if self._server is None:
            raise Exception("Server needs to be set")
        if self._api_key is None:
            raise Exception("API key needs to be set")
        
        self._pantheon = pantheon.Pantheon(self._server, self._api_key, requestsLoggingFunction=self._logger.push_request)
        
        for e in self._elements:
            if issubclass(e.__class__, Manager):
                e.set_pantheon(self._pantheon)
                self._managers.append(e)
            if issubclass(e.__class__, Queue):
                self._queues.append(e)
            if issubclass(e.__class__, Bootstrap):
                e.set_pantheon(self._pantheon)
                self._bootstrap.append(e)
        
        self._init = True
                
    def run(self, awaited=True):
        if not self._init:
            self.init_elements()
        
        
        self._running = True
        if awaited:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.gather(*[m.run() for m in self._managers] + [b.run() for b in self._bootstrap] + [self._master()]))
        else:
            asyncio.gather(*[m.run() for m in self._managers] + [b.run() for b in self._bootstrap] + [self._master()])
            
    async def is_idle(self):
        return all([queue.empty() for queue in self._queues]) and all([await manager.is_idle() for manager in self._managers])
    
    async def _master(self):
        while True:
            #Check every 5 seconds
            await asyncio.sleep(5)
            
            # If idle twice in a row, quit
            if await self.is_idle():
                await asyncio.sleep(5)
                if await self.is_idle():
                    break
        # Send end signal in all queues
        for queue in self._queues:
            await queue.put(None)
            
        # Send stop signal in all managers
        for manager in self._managers:
            manager.stop()
        
        self._running = False
        print("quit")
            
    async def print_status(self):
        print("Current state : ")
        print("Targon : ")
        print("\tRunning : " + str(self._running))
        print("\tIdle : " + str(await self.is_idle()))
        print("Requests status in the last minute : ")
        for i,j in self._logger.get_window_stats().items():
            print("\t",i,":",j)
        for queue in self._queues:
            print(queue)
        for manager in self._managers:
            print(await manager.print_manager())
            
        print(self._pantheon)
        
    async def print_status_loop(self):
        try:
            from IPython.display import clear_output
        except:
            raise Exception("Loop is only available in notebooks")
        
        while self._running:
            await asyncio.sleep(1)
            clear_output(wait=True)
            await self.print_status()
        clear_output(wait=True)
        print("Current state : ")
        print("\tStopped")