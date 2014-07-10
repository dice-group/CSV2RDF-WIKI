from csv2rdf.database import DatabasePlainFiles
from csv2rdf.config.config import data_classified_cache_path

from csv2rdf.classification.interfaces import ClassifierInterface

class Classifier(ClassifierInterface):
    enabledClassifiers = [
                "fox",
                "dbpediaspotlight"
            ]
    def __init__(self):
        ClassifierInterface.__init__(self)
        self._initClassifiers()

    def _initClassifiers(self):
        for classifierName in self.enabledClassifiers:
            className = classifierName.capitalize()+"Classifier"
            packageName = "csv2rdf.classification."+classifierName
            localObjectName = "self."+classifierName+"Classifier"
            exec("from "+packageName+" import "+className)
            exec(localObjectName+" = "+className+"()")

    def getEntitiesWithClassesJson(self, resourceId):
        entitiesJson = []
        entities = self.getEntitiesWithClasses(resourceId)
        for entity in entities:
            structureElem = entity[0]
            entityUri = entity[1]
            print entityUri
            entityclass = entities[entity]
            entityJson = {"structureElement": structureElem,
                          "uri": entityUri,
                          "class": entityclass}
            entitiesJson.append(entityJson)
        return entitiesJson

    def getClasses(self, resourceId):
        db = DatabasePlainFiles(data_classified_cache_path + resourceId)
        if(db.is_exists(resourceId)):
            return db.loadDbase(resourceId)
        else:
            entities = set()
            for classifierName in self.enabledClassifiers:
                classifier = eval("self."+classifierName+"Classifier")
                new_entities = classifier.getEntities(resourceId)
                entities = entities.union(new_entities)
            entities = self._getClassesForEntities(entities)
            db.saveDbase(resourceId, entities)
            return entities


if __name__ == "__main__":
    #testResourceId = "8b51874e-cda8-4910-a3c0-9140e11164a3"
    testResourceId = "5e8ff30e-86c2-42ff-889e-c950f9d7e8c4"
    classifier = Classifier()
    classes = classifier.getClasses(testResourceId)
    import pprint
    pprinter = pprint.PrettyPrinter()
    pprinter.pprint(classes)
    #print classes
