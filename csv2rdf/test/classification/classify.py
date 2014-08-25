from csv2rdf.classification.classify import Classifier
from csv2rdf.test.interfaces import TestInterface

class TestClassifier(TestInterface):
    def __init__(self):
        self.classifier = Classifier()
        pass

    def classifyRandom20(self):
        import pprint
        pprinter = pprint.PrettyPrinter()
        resourceIds = self.getRandom20Resources()
        for resourceId in resourceIds:
            print resourceId
            try:
                pprinter.pprint(self.classifier.getClasses(resourceId))
            except BaseException as e:
                print str(e)

if __name__ == "__main__":
    testClassifier = TestClassifier()
    testClassifier.classifyRandom20()
