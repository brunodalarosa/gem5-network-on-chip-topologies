class Router(object):
    description="Test Router"

    def __init__(self,value):
        self._value = value

    def toString(self):
        print (self._value)

class Topology(object):
    description="Test Topology"

    def __init__(self):
        self._test = "testing"

    def makeTopology(self,options):
        test = self._test

        routers = [Router(i) for i in range(10)]

        print(test)

        for i in range(10):
            routers[i].toString()
