class MatchlistParser:
    
    def __init__(self, timestamp_minimum=None, timestamp_maximum=None, autopaginate=False, input_queue=None, output_queue=None, callback=None):
        
        if not timestamp_minimum is None and not timestamp_maximum is None:
            if timestamp_minimum > timestamp_maximum:
                raise Exception("timestamp_minimum must be lesser than timestamp_maximum")
                
                
        if autopaginate and input_queue is None:
            raise Exception("autopaginate requires an input queue, the one feeding the matchlist callers")
            
        self._timestamp_minimum = timestamp_minimum
        self._timestamp_maximum = timestamp_maximum
        self._autopaginate = autopaginate
        self._input_queue = input_queue
        self._output_queue = output_queue
        self._callback = callback
        
    def set_output_queue(self, output_queue):
        self._output_queue = output_queue
        
    def set_input_queue(self, input_queue):
        self._input_queue = input_queue
        
    def set_callback(self, callback):
        self._callback = callback
        
        
    async def parse(self, input_value, data):
        try:
            accountId, beginIndex = input_value
        except:
            accountId = input_value
            bneginIndex = 0
        
        #If at least one match in the list
        if data['totalGames'] > 0:
            # Extracting matchIds from the matchlist and sending them in the queue
            # Filtering if needed
            for match in data['matches']:
                # If the match is too old, the following ones will be older
                if not self._timestamp_minimum is None and match["timestamp"] < self._timestamp_minimum:
                    break
                # If match is too recent go back in time
                if not self._timestamp_maximum is None and match["timestamp"] > self._timestamp_maximum:
                    continue
                await self._output_queue.put(match['gameId'])
                
                if not self._callback is None:
                    self._callback(match['gameId'])
                
            if self._autopaginate:
                # If the last match of the list is too old, the following pages will be too old too
                if not self._timestamp_minimum and data['matches'][-1]["timestamp"] < self._timestamp_minimum:
                    return
                await self._input_queue.put((accountId, beginIndex+100))
                
                
class MatchParser:
    
    ALLOWED_PLAYER_ID = ["currentAccountId","accountId","summonerId"]
    
    def __init__(self, player_id_target="currentAccountId", output_queue=None, callback=None):
        
        if not player_id_target in self.ALLOWED_PLAYER_ID:
            raise Exception("Invalid player_id_target")
            
        self._player_id_target = player_id_target
        self._output_queue = output_queue
        self._callback = callback
        
        
    def set_output_queue(self, output_queue):
        self._output_queue = output_queue
        
    def set_callback(self, callback):
        self._callback = callback
        
    async def parse(self, input_value, data):
        # For each player
        for p in (data['participantIdentities']):
            # Just in case
            try:
                # Kick out bots
                if not p['player']['currentAccountId'] == "0":
                    await self._output_queue.put(p['player'][self._player_id_target])
                    if not self._callback is None:
                        self._callback(p['player'][self._player_id_target])
            except:
                pass