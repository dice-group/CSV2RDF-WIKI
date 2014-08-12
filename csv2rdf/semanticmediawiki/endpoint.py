from csv2rdf.config.config import wiki_sparql_url
from csv2rdf.config.config import wiki_base_url
from csv2rdf.config.config import wiki_csv2rdf_namespace

import requests
import RDF

class SMWEndpoint(object):
    propertyDatasetId = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ADatasetId"
    propertyDatasetUrl = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ADatasetUrl"
    propertyDatasetLabel = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ADatasetLabel"
    propertyResourceId = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3AResourceId"
    propertyResourceLabel = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3AResourceLabel" 
    propertyResourceUrl = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3AResourceUrl"
    propertyCsvFileSize = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ACsv_file_size"
    propertyCsvNumberOfColumns = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ACsv_number_of_columns"
    propertyHasProperty = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3AHas_property"
    propertyRdfLastSparqlifiedDate = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ARdf_last_sparqlified"
    propertyRdfLastSparqlified = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3ARdf_last_sparqlified-23aux"
    propertyModificationDate = "http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3AModification_date-23aux"
    propertyWikiPageModificationDate = "http://semantic-mediawiki.org/swivt/1.0#wikiPageModificationDate"
    propertyPage = "http://semantic-mediawiki.org/swivt/1.0#page"
    propertyLabel = "http://www.w3.org/2000/01/rdf-schema#label"
    propertyWikiNamespace = "http://semantic-mediawiki.org/swivt/1.0#wikiNamespace"

    def __init__(self):
        self.model = RDF.Model()
        self.parser = RDF.NTriplesParser()

    def execute(self, query):
        ntriplesString = self._sendPostToVirtuoso(query)
        self.parser.parse_string_into_model(self.model, ntriplesString, 'http://localhost/')
        return self.model

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


    def _genResourceQuery(self, resourceUri):
        return "CONSTRUCT {%s ?p ?o .} WHERE { %s ?p ?o.}" % (resourceUri, resourceUri, )

    def _genPropertyQuery(self, propertyUri):
        return "CONSTRUCT {?s ?p ?o .} WHERE { ?s ?p ?o . ?s <%s> %s}" % (self.propertyHasProperty, propertyUri,)

    def _genDatasetQuery(self, datasetUri):
        return "CONSTRUCT {?s ?p ?o .} WHERE { ?s ?p ?o . ?s <%s> <%s>}" % (self.propertyDatasetId, datasetUri,)

    def fetchResource(self, resourceId):
        resourceUri = self._genResourceUri(resourceId)
        queryString = self._genResourceQuery(resourceUri)
        print queryString
        resourceMetaString = self.execute(queryString)
        return self.model

    def findSimilarResources(self, resourceId):
        resourceModel = self.fetchResource(resourceId)
        resourcePropertiesQuery = RDF.Query("SELECT ?o WHERE {?s <http://wiki.publicdata.eu/wiki/Special:URIResolver/Property-3AHas_property> ?o.}")
        resourceProperties = resourcePropertiesQuery.execute(resourceModel)
        for resourceProperty in resourceProperties:
            prop = "<%s>" %(resourceProperty['o'],)
            query = self._genPropertyQuery(prop)
            print query
            res = self.execute(query)
            import ipdb; ipdb.set_trace()

    def findResourceInSameDataset(self, resourceId):
        """
            Returns other resources in the dataset.
            We assume that all resources in the same dataset have the same structure.
        """
        similarResources = []

        resourceModel = self.fetchResource(resourceId)
        resourceDatasetQuery = RDF.Query("SELECT ?o WHERE {?s <%s> ?o.}"%(self.propertyDatasetId,))
        resourceDataset = str(resourceDatasetQuery.execute(resourceModel).next()['o'])
        similarResourcesQuery = self._genDatasetQuery(resourceDataset)
        model = RDF.Model()
        parser = RDF.NTriplesParser()
        ntriplesString = self._sendPostToVirtuoso(similarResourcesQuery)
        parser.parse_string_into_model(model, ntriplesString, 'http://localhost/')
        distinctResourceUris = RDF.Query("SELECT DISTINCT ?s WHERE {?s ?p ?o.}")
        similarResourcesResult = distinctResourceUris.execute(model)
        for resource in similarResourcesResult:
            similarResources.append(str(resource['s']))
        
        return similarResources

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
    print endpoint.findResourceInSameDataset(resourceId)
