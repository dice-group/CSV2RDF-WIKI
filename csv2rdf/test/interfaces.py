import os.path

class TestInterface(object):
    def __init__(self):
        pass

    def getRandom20Resources(self):
        resourceIds = []
        random20filepath = os.path.join(os.path.dirname(__file__), 'random20resourceids')
        for line in open(random20filepath, 'rU').readlines():
            resourceIds.append(line.rstrip())
        return resourceIds
