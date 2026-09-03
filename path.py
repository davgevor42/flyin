class peth:

    def __init__(self, graph):
        self.graph = graph
    
    def find_path(self, start, end):
        distance = {}
        previous = {}
        for zone in self.graph.zones.values():
            
