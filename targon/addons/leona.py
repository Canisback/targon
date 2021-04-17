from solari import Leona as true_Leona


class Leona(true_Leona):
    
    def __init__(self, stats):
        super().__init__(stats)
        
    def push_match(self, matchId, data):
        super().push_match(data)