from csv2rdf.classification.interfaces import ClassifierInterface
from csv2rdf.classification.interfaces import ClassifierDataInterface
from lovpy.lovscraper import LovScraper

class LovClassifier(ClassifierInterface,
                    ClassifierDataInterface):
    def __init__(self):
        ClassifierInterface.__init__(self)
        ClassifierDataInterface.__init__(self)

    def _recognizeEntities(self, text):
        (text, output, log) = self.fox.recognizeText(text)
        return (text, output, log)

    def getEntities(self, resourceId):
        fox = self._recognizeEntitiesResource(resourceId)
        entitiesRecognized = set()
        for structuralElement in fox:
            structuralElementName = structuralElement.keys()[0]
            (text, entities, log) = structuralElement[structuralElementName]
            entities = json.loads(entities)
            if( '@graph' in entities ):
                for entity in entities['@graph']:
                    entitiesRecognized.add((structuralElementName, entity['means']))
        return entitiesRecognized

if __name__ == "__main__":
    testResourceId = "5e8ff30e-86c2-42ff-889e-c950f9d7e8c4"
    lovClassifier = LovClassifier()
    print lovClassifier.getEntitiesWithClasses(testResourceId)
