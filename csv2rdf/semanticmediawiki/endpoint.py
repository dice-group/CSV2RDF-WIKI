import requests
import RDF

from csv2rdf.config.config import wiki_sparql_url

class SMWEndpoint(object):
    def __init__(self):
        pass

    def execute(self, query):
        model = RDF.Model()
        parser = RDF.NTriplesParser()
        ntriplesString = self._sendPostToVirtuoso(query)
        parser.parse_string_into_model(model, ntriplesString, 'http://localhost/')
        return model

    def _sendPostToVirtuoso(self, query):
        params = {
                    'default-graph-uri': '',
                    'query': query,
                    'should-sponge': '',
                    'format': 'text/plain',
                    'timeout': 0,
                    'debug': 'on'
                 }

        r = requests.post(wiki_sparql_url, data=params)
        return r.text
    
if __name__ == "__main__":
    resourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    endpoint = SMWEndpoint()
    print endpoint.getResourcesFromDatasetIds(resourceId)
