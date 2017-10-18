import random
class FakeInstr(object):

    def measure(self):
        return random.random()


    def __init__(self):
        pass

    def __repr__(self):
        return 'FakeInstr()'

    def __str__(self):
        return 'Fake Instrument'
    
