import spotlight

from csv2rdf.classification.interfaces import ClassifierInterface
from csv2rdf.classification.interfaces import ClassifierDataInterface

class DbpediaspotlightClassifier(ClassifierInterface,
                          ClassifierDataInterface):
    def __init__(self):
        ClassifierInterface.__init__(self)
        ClassifierDataInterface.__init__(self)

    def _recognizeEntities(self, text):
        annotationServiceUri = 'http://spotlight.dbpedia.org/rest/annotate'
        confidence = 0.5
        support = 20
        return spotlight.annotate(annotationServiceUri, text, confidence=confidence, support=support)

    def getEntities(self, resourceId):
        spotlight = self._recognizeEntitiesResource(resourceId)
        entitiesRecognized = set()
        for structuralElement in spotlight:
            structuralElementName = structuralElement.keys()[0]
            entities = structuralElement[structuralElementName]
            for entity in entities:
                entitiesRecognized.add((structuralElementName,entity['URI']))
        return entitiesRecognized

if __name__ == "__main__":
    testResourceId = "5e8ff30e-86c2-42ff-889e-c950f9d7e8c4"
    spotlightClassifier = DbpediaspotlightClassifier()
    print spotlightClassifier.getEntitiesWithClasses(testResourceId)
