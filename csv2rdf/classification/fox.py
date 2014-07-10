import json

import foxpy.fox
from csv2rdf.classification.interfaces import ClassifierInterface
from csv2rdf.classification.interfaces import ClassifierDataInterface

class FoxClassifier(ClassifierInterface,
                    ClassifierDataInterface):
    def __init__(self, foxlight=4):
        """
            TODO: feed scmc.eu to spotlight
        """
        ClassifierInterface.__init__(self)
        ClassifierDataInterface.__init__(self)
        self.fox = foxpy.fox.Fox(foxlight) #foxlight stands for NER method, see Fox class for details

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
    foxClassifier = FoxClassifier()
    print foxClassifier.getEntitiesWithClasses(testResourceId)
