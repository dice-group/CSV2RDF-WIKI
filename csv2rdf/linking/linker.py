import urllib

from csv2rdf.interfaces.data import DataInterface

from limespy.confgen import LimesConfigGenerator
from limespy.limes import LimesRunner

from csv2rdf.prefixcc import PrefixCC

class LimesCsvLinker(DataInterface):
    sourceUri = "/home/ivan/Soft/Installed/LIMES-test/cities.csv"
    sourceProperty = "City AS lowercase"
    sourceType = "csv"
    sourceVar = "?x"
    sourceRestriction = ""
    targetUri = "http://dbpedia.org/sparql"
    targetProperty = "rdfs:label AS nolang->lowercase"
    targetType = "sparql"
    targetVar = "?y"
    targetRestriction = "?y rdf:type dbpedia:City"
    metricString = "levenshtein(x.City, y.rdfs:label)"
    acceptanceThreshold = "0.95"
    acceptanceOutfile = "foo.nt"
    acceptanceRelation = "owl:sameAs"
    reviewThreshold = "0.9"
    reviewOutfile = "foo2.nt"
    reviewRelation = "owl:sameAs"

    def __init__(self, resourceId):
        DataInterface.__init__(self)
        self.confgen = LimesConfigGenerator()

        self.setSourceUri(resourceId)
        self.mappings = self._getMappings(resourceId)
        self.mappings.init_mappings_only()
        self.setSourceProperty(resourceId)

        self.mapping = self.mappings.get_mapping_by_name('csv2rdf-interface-generated')
        class_ = urllib.unquote(self.mapping['class'])
        self.setTargetRestriction(class_)

        self.setMetricString()
        self.setAcceptanceConditions()
        self.setReviewConditions()

    def setSourceUri(self, resourceId):
        self.sourceUri = self._getFilePath(resourceId)

    def setSourceProperty(self, resourceId):
        header = self.mappings.get_header_by_name('csv2rdf-interface-generated')
        originalHeader = self._getOriginalHeader(resourceId)
        firstCol = originalHeader[0]['label']
        self.colToMatch = firstCol
        self.sourceProperty = "%s AS lowercase" % (self.colToMatch, )

    def setTargetRestriction(self, class_):
        prefixcc = PrefixCC()
        #class_ = prefixcc.reverse_lookup(class_)
        self.targetRestriction = "?y rdf:type &lt;%s&gt;" % (class_, )

    def setMetricString(self):
        self.metricString = "levenshtein(x.%s, y.rdfs:label)"%self.colToMatch

    def setAcceptanceConditions(self):
        self.acceptanceOutfile = "/tmp/foo.nt"

    def setReviewConditions(self):
        self.reviewOutfile = "/tmp/foo2.nt"

    def linkCsv(self):
        config = self.generateLimesConfig()
        filepath ='/tmp/limeslinkcsvtodbpedia.xml' 
        f = open(filepath, 'wb+')
        f.write(config)
        f.close()
        limesRunner = LimesRunner()
        return limesRunner.run(filepath)

    def generateLimesConfig(self):
        return self.confgen.generateMinimalConfig(self.sourceUri, self.sourceProperty, self.sourceType, self.sourceVar, self.sourceRestriction,
                                             self.targetUri, self.targetProperty, self.targetType, self.targetVar, self.targetRestriction,
                                             self.metricString, 
                                             self.acceptanceThreshold, self.acceptanceOutfile, self.acceptanceRelation,
                                             self.reviewThreshold, self.reviewOutfile, self.reviewRelation)


if __name__ == "__main__":
    testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    linker = LimesCsvLinker(testResourceId)
    print linker.linkCsv()
    #print linker.generateLimesConfig()
