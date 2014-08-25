import RDF

from csv2rdf.semanticmediawiki.endpoint import SMWEndpoint
from csv2rdf.semanticmediawiki.querygen import SMWQueryGenerator

class SMWQuery(object):
    def __init__(self):
        self.endpoint = SMWEndpoint()
        self.querygen = SMWQueryGenerator()

    def fetchResource(self, resourceId):
        rdfModel = self.endpoint.execute(self.querygen.getResourceQuery(resourceId))
        return rdfModel 

    def fetchResourceProperties(self, resourceId):
        resourceProperties = []
        resource = self.fetchResource(resourceId)
        resourcePropertiesQuery = RDF.Query(self.querygen.getResourcePropertiesQuery())
        for resourceProperty in resourcePropertiesQuery.execute(resource):
            resourceProperties.append("<%s>"%(resourceProperty['o']))
        return resourceProperties

    def fetchResourceDataset(self, resourceId):
        resource = self.fetchResource(resourceId)
        resourceDatasetQuery = RDF.Query(self.querygen.getResourceDatasetQuery())
        resourceDataset = "<%s>" %(str(resourceDatasetQuery.execute(resource).next()['o']),)
        return resourceDataset

    def fetchAllResourcesFromDataset(self, resourceId):
        datasetUri = self.fetchResourceDataset(resourceId)
        resourcesFromDatasetQuery = self.querygen.getResourceByDatasetUriQuery(datasetUri)
        return self.endpoint.execute(resourcesFromDatasetQuery)

    def fetchAllResourceIdsFromDataset(self, resourceId):
        resourceIds = []
        resources = self.fetchAllResourcesFromDataset(resourceId)
        resourceDistinctSubjectQuery = RDF.Query(self.querygen.getDistinctSubjectQuery())
        for resource in resourceDistinctSubjectQuery.execute(resources):
            resourceId = self.querygen._convertSparqlIdToResourceId(str(resource['s']).split("Csv2rdf-")[-1].lower())
            resourceIds.append(resourceId)
        return resourceIds

if __name__ == "__main__":
    resourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    smwquery = SMWQuery()
    resource = smwquery.fetchAllResourceIdsFromDataset(resourceId)
    import ipdb; ipdb.set_trace()


