class Bootstrap:
    
    def __init__(self, output_queue=None, strategies={}, n_callers=10):
        
        self._strategies = strategies
        self._n = n_callers
        
        self._output_queue = output_queue
        
        self._data_found = False
        
        
            
    def set_pantheon(self, pantheon):
        self._pantheon = pantheon