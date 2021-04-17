import requests
from ..callers import Caller
from .bootstrap import Bootstrap

class LeagueIdSeeder(Bootstrap):
    
    def __init__(self, output_queue=None, strategies={}, n_callers=10):
        
        super().__init__(output_queue, strategies, n_callers)
        
    def set_output_queue(self, output_queue):
        self._output_queue = output_queue
        
    
    async def run(self):
        server = self._pantheon._server
        r = requests.get("https://canisback.com/leagueId/matchlist_{}.json".format(server))
        
        if r.status_code == 404:
            raise Exception("This server is not supported for seeding leagueIds, please try another seeding method.")
            
        if r.status_code == 200:
            for i in r.json():
                self._output_queue.put_nowait(i)
        
        else:
            raise Exception("Something went wrong during the sseding.")