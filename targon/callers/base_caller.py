from pantheon.utils import exceptions as exc
import sys
import asyncio
import time

from enum import Enum

class CallFailureStrategy(Enum):
    RETRY="retry"
    IGNORE="ignore"
    SAVE="save"
    EXIT="exit"
    
class CallerState(Enum):
    INITIALIZED="Initialized"
    WAITING_INPUT="Waiting input"
    WAITING_CALL="Waiting call"
    WAITING_CALLBACK="Waiting callback"
    STOPPED="Stopped"



class Caller:
    
    DEFAULT_STRATEGIES = {
        exc.NotFound : CallFailureStrategy.IGNORE,
        exc.RateLimit : CallFailureStrategy.RETRY,
        exc.ServerError : CallFailureStrategy.RETRY,
        exc.Timeout : CallFailureStrategy.RETRY,
        exc.Forbidden : CallFailureStrategy.EXIT,
        exc.Unauthorized : CallFailureStrategy.EXIT,
        exc.BadRequest : CallFailureStrategy.EXIT
    }
    
    def __init__(self, function_to_call, input_queue, input_args=None, callback=None, strategies={}):
        
        self._strategies = self.DEFAULT_STRATEGIES
        for s in strategies:
            self._strategies[s] = strategies[s]
        
        self._call = function_to_call
        self._input_queue = input_queue
        self._input_args = input_args
        
        
        if callback is None:
            self._callback = self.dismiss_callback
        elif type(callback) == list:
            self._callback_functions = callback
            self._callback = self.handle_callbacks
        else:
            self._callback_function = callback
            self._callback = self.handle_callback
        
        self._state = CallerState.INITIALIZED
        self._call_history = []
        self._last_call_time = None
        
    async def dismiss_callback(self, input_value, data):
        pass
        
    async def handle_callback(self, input_value, data):
        (await self._callback_function(input_value, data)) if asyncio.iscoroutinefunction(self._callback_function) else self._callback_function(input_value, data)
        
    async def handle_callbacks(self, input_value, data):
        for callback_function in self._callback_functions:
            (await callback_function(input_value, data))  if asyncio.iscoroutinefunction(callback_function) else callback_function(input_value, data)
        
    async def run(self):
        # Needs to run until stop signal
        while True:
            
            #Get accountId from queue
            self._state = CallerState.WAITING_INPUT
            self._input_value = await self._input_queue.get()

            #Leave if the stop signal is sent
            if self._input_value is None:
                self._state = CallerState.STOPPED
                await self._input_queue.put(None)
                break

            try:
                # Use the call function on the input value, and with the args if needed
                self._state = CallerState.WAITING_CALL
                data = await (self._call(self._input_value) if self._input_args is None else self._call(self._input_value, self._input_args))
                self._last_call_time = time.time()
                self._call_history.append({"value":self._input_value,"timestamp":self._last_call_time})
                
                # Sending the data to the callback
                self._state = CallerState.WAITING_CALLBACK
                await self._callback(self._input_value, data)
                
            except Exception as e:
                '''import traceback
                traceback.print_exc()'''
                
                self._last_call_time = time.time()
                # If it's an handled strategy
                if type(e) in self._strategies:
                    s = self._strategies[type(e)]
                    
                    # Retry strategy send the input_value in the queue again
                    if s == CallFailureStrategy.RETRY:
                        await self._input_queue.put(self._input_value)
                    
                    # Exit strategy when something wen wrong
                    elif s == CallFailureStrategy.EXIT:
                        return

    
    def __str__(self):
        return "Caller on {} / State : {} / Last call time : {}".format(self._call.__name__, self._state.value, self._last_call_time)
    
    def get_last_call_since(self):
        return time.time() - self._last_call_time if not self._last_call_time is None else 9999999
    