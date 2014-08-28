from csv2rdf.database import DatabasePlainFiles
from csv2rdf.config.config import data_classified_cache_path

from csv2rdf.classification.interfaces import ClassifierInterface

class Classifier(ClassifierInterface):
    enabledClassifiers = [
                "fox",
                "dbpediaspotlight"
            ]
    def __init__(self, resourceId=None):
        if(not (resourceId != None and 
           self.isCached(resourceId))):
            ClassifierInterface.__init__(self)
            self._initClassifiers()

    def _initClassifiers(self):
        for classifierName in self.enabledClassifiers:
            className = classifierName.capitalize()+"Classifier"
            packageName = "csv2rdf.classification."+classifierName
            localObjectName = "self."+classifierName+"Classifier"
            exec("from "+packageName+" import "+className)
            exec(localObjectName+" = "+className+"()")

    def getClassesJson(self, resourceId):
        entitiesJson = []
        entities = self.getClasses(resourceId)
        for entity in entities:
            structureElem = entity[0]
            entityUri = entity[1]
            entityclass = entities[entity]
            entityJson = {"structureElement": structureElem,
                          "uri": entityUri,
                          "class": entityclass}
            entitiesJson.append(entityJson)
        return entitiesJson

    def isCached(self, resourceId):
        db = DatabasePlainFiles(data_classified_cache_path + resourceId)
        if(db.is_exists(resourceId)):
            return True 
        else:
            return False

    def getClasses(self, resourceId):
        db = DatabasePlainFiles(data_classified_cache_path + resourceId)
        if(self.isCached(resourceId)):
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
    testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    classifier = Classifier(testResourceId)
    classes = classifier.getClassesJson(testResourceId)
    import pprint
    pprinter = pprint.PrettyPrinter()
    pprinter.pprint(classes)
    #print classes
