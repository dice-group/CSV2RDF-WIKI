from csv2rdf.propertymapping.lodstats import LodstatsMapper
from csv2rdf.test.interfaces import TestInterface

class TestLodstatsMapper(TestInterface):
    def __init__(self):
        self.lodstatsMapper = LodstatsMapper()
        pass

    def maprandom20(self):
        resourceIds = self.getRandom20Resources()
        for resourceId in resourceIds[4:]:
            print resourceId
            try:
                mappings = self.lodstatsMapper.getMappings(resourceId)
                import pprint
                pprinter = pprint.PrettyPrinter()
                pprinter.pprint(mappings)
            except BaseException as e:
                print str(e)

if __name__ == "__main__":
    testlm = TestLodstatsMapper()
    testlm.maprandom20()
