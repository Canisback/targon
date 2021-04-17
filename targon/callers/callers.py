from .base_caller import Caller, CallerState
import asyncio
import time

class Manager:
    
    def __init__(self, input_queue=None, callback=None, strategies={}, n_callers=5):
        
        self._input_queue = input_queue
        self._callback = callback
        self._strategies = strategies
        self._n = n_callers
        
        self._callers_state = {cs:0 for cs in CallerState}
        self._idle_callers = 0
        self._callers_state_lock = asyncio.Lock()
        
        self._running = False
            
    def set_pantheon(self, pantheon):
        self._pantheon = pantheon
            
    def set_callback(self, callback):
        self._callback = callback
            
    def set_n_callers(self, n_callers):
        self._n = n_callers
            
    def add_callback(self, callback):
        if self._callback is None:
            self._callback = callback
        elif not type(self._callback) == list:
            self._callback = [self._callback, callback]
        else:
            self._callback.append(callback)
            
    def set_input_queue(self, input_queue):
        self._input_queue = input_queue
        
    def stop(self):
        self._running = False
        
    async def run(self):
        if self._input_queue is None:
            raise Exception("An input queue must be set")
        self._callers = [self.create_caller() for _ in range(self._n)]
        for c in self._callers:
            self._callers_state[c._state] += 1
        self._running = True
        await asyncio.gather(*([c.run() for c in self._callers] + [self.master()]))
        
    async def get_callers_state(self):
        async with self._callers_state_lock:
            return self._callers_state
        
    async def is_idle(self):
        c_state = await self.get_callers_state()
        return c_state[CallerState.WAITING_INPUT] == self._n
    
    async def master(self):
        while self._running:
            await asyncio.sleep(1)
            async with self._callers_state_lock:
                t = time.time()
                self._callers_state = {cs:0 for cs in CallerState}
                self._idle_callers = 0
                for c in self._callers:
                    self._callers_state[c._state] += 1
                    if c.get_last_call_since() > 15:
                        self._idle_callers += 1


class Match(Manager):
    
    def __init__(self, input_queue=None, callback=None, strategies={}, n_callers=5, include_timeline=False):
        
        super().__init__(input_queue, callback, strategies, n_callers)
        
        self._include_timeline = include_timeline
        
    def create_caller(self):
        func = self.get_match_timeline if self._include_timeline else self._pantheon.getMatch
        return Caller(func, self._input_queue, callback=self._callback, strategies=self._strategies)
        
            
    async def get_match_timeline(self, matchId):
        match, timeline = await asyncio.gather(*[
            self._pantheon.getMatch(matchId), 
            self._pantheon.getTimeline(matchId)
        ])
        match["timeline"] = timeline
        return match
    
    def get_str_status(self):
        s = "Match callers : \n"
        self._callers_state = {cs:0 for cs in CallerState}
        for c in self._callers:
            self._callers_state[c._state] += 1
        s += str(self._callers_state)
            
        
    
    def __str__(self):
        if hasattr(self, "_callers"):
            s = "Match callers : \n"
            s += "\n".join([str(c) for c in self._callers])
            return s
        return "Match callers initialized"
        
    
    async def print_manager(self):
        if hasattr(self, "_callers"):
            s = "Match callers : "
            c_state = await self.get_callers_state()
            for c in c_state:
                s += "{} : {:>4} | ".format(c.value, c_state[c])
            return s
        return "Match callers initialized"
    
    
class Matchlist(Manager):
    
    def __init__(self, input_queue=None, callback=None, strategies={}, n_callers=5, input_args=None):
        
        super().__init__(input_queue, callback, strategies, n_callers)
        
        self._input_args = input_args
    
            
    def set_input_args(self, input_args):
        self._input_args = input_args
        
    def create_caller(self):
        return Caller(self._pantheon.getMatchlist, self._input_queue, input_args=self._input_args, callback=self._callback, strategies=self._strategies)
        
    async def get_matchlist(self, value):
        accountId, begin_index = value
        params = self._input_args
        params["beginIndex"] = begin_index
        data = await self._pantheon.getMatchlist(accountId, params=params)
        
    
    def __str__(self):
        if hasattr(self, "_callers"):
            s = "Matchlist callers : \n"
            s += "\n".join([str(c) for c in self._callers])
        return "Matchlist callers initialized"
        
    
    async def print_manager(self):
        if hasattr(self, "_callers"):
            s = "Matchlist callers : " 
            c_state = await self.get_callers_state()
            for c in c_state:
                s += "{} : {:>4} | ".format(c.value, c_state[c])
            return s
        return "Matchlist callers initialized"