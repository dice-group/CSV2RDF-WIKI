from csv2rdf.propertymapping.mapper import Mapper

class DbpediaMapper(Mapper):
    def __init__(self):
        pass

    def getMappings(self, resourceId):
        headers = self._getHeaders(resourceId)
        entities = self._getEntities(resourceId)
        print headers

if __name__ == "__main__":
    testResourceId = "8b51874e-cda8-4910-a3c0-9140e11164a3"
    mapper = DbpediaMapper()
    mapper.getMappings(testResourceId)
