from csv2rdf.config.config import wiki_sparql_url
from csv2rdf.config.config import wiki_base_url
from csv2rdf.config.config import wiki_csv2rdf_namespace

import requests
import RDF

class SMWEndpoint(object):
    def __init__(self):
        pass

    def query(self, query):
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

    def fetchResource(self, resourceId):
        resourceUri = self._genResourceUri(resourceId)
        queryString = "CONSTRUCT {%s ?p ?o .} WHERE { %s ?p ?o.}" % (resourceUri, resourceUri, )
        model = RDF.Model()
        parser = RDF.NTriplesParser()
        resourceMetaString = self.query(queryString)
        parser.parse_string_into_model(model, resourceMetaString, 'http://localhost/')
        ser = RDF.NTriplesSerializer()
        modelString = ser.serialize_model_to_string(model)
        import ipdb; ipdb.set_trace()

    def _convertResourceIdToSparql(self, resourceId):
        resourceId = resourceId.split("-")
        resourceId[0] = "3A"+resourceId[0]
        for num, _id in enumerate(resourceId[1:]):
            resourceId[num + 1] = "2D"+_id
        return "-".join(resourceId)

    def _genResourceUri(self, resourceId):
        sparqlId = self._convertResourceIdToSparql(resourceId)
        url = "<%s/wiki/Special:URIResolver/%s-%s>" % (wiki_base_url, wiki_csv2rdf_namespace[:-1], sparqlId, )
        return url
    
if __name__ == "__main__":
    resourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    endpoint = SMWEndpoint()
    print endpoint.fetchResource(resourceId)
