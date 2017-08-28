class Vector2(object):
    """A basic vector 2 class"""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return 'Vector 2 with values x:{} y:{}'.format(self.x,  self.y)