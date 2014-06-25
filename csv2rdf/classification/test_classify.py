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

    def getClassifiedFullpath(self):
        from os.path import join
        classied = [ join(data_classified_path, f) for f in self.getFilenamesFromFolder(data_classified_path)]
        return classied

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

    def analyseClassified(self):
        classifiedList = self.getClassifiedFullpath()
        for path in classifiedList:
            print path
            classified = pickle.load(open(path, 'rU'))
            for item in classified:
                for key in item.keys():
                    text = item[key][0]
                    output = item[key][1]
                    print key + "\n" +text+"\n"+output 
            import ipdb; ipdb.set_trace()
            break


if __name__ == "__main__":
    testclassify = TestClassify()
    testclassify.classifyTop500()
    #testclassify.analyseClassified()
