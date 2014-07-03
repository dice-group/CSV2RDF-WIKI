from csv2rdf.classification.classify import Classificator
import cPickle as pickle

from csv2rdf.config.config import data_classified_path
from csv2rdf.config.config import resources_path

class TestClassify(object):
    def __init__(self):
        pass

    def getFilenamesFromFolder(self, fullpath):
        from os import listdir
        from os.path import isfile, join
        filenames = [ f for f in listdir(fullpath) if isfile(join(fullpath,f)) ]
        return filenames

    def getAvailableResourceIds(self):
        return self.getFilenamesFromFolder(resources_path)

    def getClassifiedResourceIds(self):
        return self.getFilenamesFromFolder(data_classified_path + 'neropennlp')
    
    def getEntitiesResourceIds(self):
        return self.getFilenamesFromFolder(data_classified_path + 'entities')

    def getClassifiedFullpath(self):
        from os.path import join
        classified = [ join(data_classified_path, f) for f in self.getFilenamesFromFolder(data_classified_path)]
        return classified

    def getEntitiesTop10(self):
        resourceIds = self.getAvailableResourceIds()
        classificator = Classificator()
        for resourceId in resourceIds[3:10]:
            print "processing %s" % resourceId
            try:
                classified = classificator.getEntities(resourceId)
                pickle.dump(classified, open(data_classified_path + 'entities/' + resourceId, 'wb'))
            except BaseException as e:
                print str(e)
            break


    def classifyTop500(self):
        resourceIds = self.getAvailableResourceIds()
        classificator = Classificator()
        for resourceId in resourceIds[:500]:
            print "processing %s" % resourceId
            try:
                classified = classificator.classifyResource(resourceId)
                pickle.dump(classified, open(data_classified_path + resourceId, 'wb'))
            except BaseException as e:
                print str(e)

    def classifyTheSame(self):
        resourceIds = self.getClassifiedResourceIds()
        classificator = Classificator(4) #number is for foxlight
        for resourceId in resourceIds:
            print "processing %s" % resourceId
            try:
                classified = classificator.classifyResource(resourceId, classifierName="Spotlight")
                pickle.dump(classified, open(data_classified_path + 'spotlight/' + resourceId, 'wb'))
            except BaseException as e:
                print str(e)

    def analyseClassified(self):
        classifiedList = self.getClassifiedFullpath()
        for path in classifiedList:
            print path
            self.printClassified(path)

    def printClassified(self, path):
        classified = pickle.load(open(path, 'rU'))
        for item in classified:
            for structureElement in item.keys():
                print structureElement.encode('utf-8')
                for annotationItem in item[structureElement]:
                    if(type(annotationItem) is unicode):
                        print annotationItem.encode('utf-8')
                    elif(type(annotationItem) is dict):
                        for item in annotationItem:
                            print "%s : %s" % (item.encode('utf-8'), str(annotationItem[item]).encode('utf-8'))
        print ""

    def analyseOne(self, resourceId="c4001b71-dec7-403c-a5df-bc55ce070cb0"):
        from subprocess import Popen
        from subprocess import PIPE
        findCommand = "find %s -name %s" % (data_classified_path, resourceId)
        findCommand = findCommand.split()
        filesToAnalyse = Popen(findCommand, stdout=PIPE).stdout.read()
        filesToAnalyse = filesToAnalyse.split()
        for path in filesToAnalyse:
            print path
            self.printClassified(path)

    def analyseEntities(self):
        resourceIds = self.getEntitiesResourceIds()
        for resourceId in resourceIds:
            entities = pickle.load(open(data_classified_path + 'entities/' + resourceId, 'rU'))
            for entityUri in entities:
                if(not entityUri.startswith('http://scms.eu')):
                    print entityUri

if __name__ == "__main__":
    testclassify = TestClassify()
    testclassify.analyseEntities()
    #testclassify.getEntitiesTop10()
    #testclassify.analyseOne()
    #testclassify.classifyTop500()
    #testclassify.classifyTheSame()
    #testclassify.analyseClassified()
