class Saver:
    
    def __init__(self):
        self._values = []
        
    def save(self, item):
        self._values.append(item)
        
    def get(self):
        return self._values 
    
    def __str__(self):
        return "Elements saved : {}".format(len(self._values))