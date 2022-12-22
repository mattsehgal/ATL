BLANK = 0
GREEN = 1


class State:
    
    def __init__(self, props, player=None, connections=None):
        self.player = player
        self.props = props
        self.connections = connections
        self.color = BLANK

    def __repr__(self):
        return repr(f'State | Player: {self.player} | Props: {self.props} | Connections: {self.connections}')
        
    def connect(self, alt_state):
        if self.connections is None:
            self.connections = alt_state
        elif alt_state not in self.connections:
            self.connections.append(alt_state)
    
    def fill(self):
        self.color = GREEN
        pass
    
    def clear(self):
        self.color = BLANK
        pass
