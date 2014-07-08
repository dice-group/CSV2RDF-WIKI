from csv2rdf.tabular.mapping import Mapping
from csv2rdf.classification.classify import Classifier

class Mapper(object):
    def __init__(self):
        pass

    def _getHeaders(self, resourceId):
        mapping = Mapping(resourceId)
        return mapping.get_mapping_headers()

    def _getEntities(self, resourceId):
        classifier = Classifier()
        return classifier.getEntitiesWithClassesJson(resourceId)
