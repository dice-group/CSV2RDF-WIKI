from csv2rdf.config.config import wiki_base_url
from csv2rdf.config.config import wiki_csv2rdf_namespace

class SMWQueryGenerator(object):
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

    #####################
    # Textual Query Gen #
    #####################

    def getResourceQuery(self, resourceId):
        resourceUri = self._genResourceUri(resourceId)
        return "CONSTRUCT {%s ?p ?o .} WHERE { %s ?p ?o.}" % (resourceUri, resourceUri, )

    def getResourceByPropertyQuery(self, propertyUri):
        return "CONSTRUCT {?s ?p ?o .} WHERE { ?s ?p ?o . ?s <%s> %s}" % (self.propertyHasProperty, propertyUri,)

    def getResourceByDatasetUriQuery(self, datasetUri):
        return "CONSTRUCT {?s ?p ?o} WHERE {?s <%s> %s. ?s ?p ?o.}" % (self.propertyDatasetId, datasetUri,)

    def getResourcePropertiesQuery(self):
        return "SELECT ?o WHERE {?s <%s> ?o.}"%(self.propertyHasProperty,)

    def getResourceDatasetQuery(self):
        return "SELECT ?o WHERE {?s <%s> ?o.}"%(self.propertyDatasetId,)

    def getDistinctSubjectQuery(self):
        return "SELECT DISTINCT ?s WHERE {?s ?p ?o .}"

    def _genResourceUri(self, resourceId):
        sparqlId = self._convertResourceIdToSparql(resourceId)
        url = "<%s/wiki/Special:URIResolver/%s-%s>" % (wiki_base_url, wiki_csv2rdf_namespace[:-1], sparqlId, )
        return url

    def _convertSparqlIdToResourceId(self, sparqlId):
        sparqlId = sparqlId.split("-")
        for num, _id in enumerate(sparqlId):
            sparqlId[num] = _id[2:]
        return "-".join(sparqlId)

    def _convertResourceIdToSparql(self, resourceId):
        resourceId = resourceId.split("-")
        resourceId[0] = "3A"+resourceId[0]
        for num, _id in enumerate(resourceId[1:]):
            resourceId[num + 1] = "2D"+_id
        return "-".join(resourceId)
