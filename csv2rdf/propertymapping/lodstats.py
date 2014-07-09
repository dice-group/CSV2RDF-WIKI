import requests
import json

from csv2rdf.propertymapping.mapper import Mapper

class LodstatsMapper(Mapper):
    def __init__(self):
        pass

    def getMappings(self, resourceId):
        headers = self._getHeaders(resourceId)
        entities = self._getEntities(resourceId)
        payload = {'headers': json.dumps(headers), 'entities': json.dumps(entities)}
        postUri = 'http://localhost:5000/property/search'
        r = requests.post(postUri, data=payload)
        content = r.json()
        return content

if __name__ == "__main__":
    #testResourceId = "8b51874e-cda8-4910-a3c0-9140e11164a3"
    testResourceId = "5e8ff30e-86c2-42ff-889e-c950f9d7e8c4"
    lodstatsmapper = LodstatsMapper()
    import pprint
    pprinter = pprint.PrettyPrinter()
    pprinter.pprint(lodstatsmapper.getMappings(testResourceId))
