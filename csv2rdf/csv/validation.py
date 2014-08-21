import re
import csv
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.tabular.mapping import Mapping

class CsvDatatypeValidator(object):
    csvDelimiter = ""
    headerLine = 0 
    csvHeader = []
    csvFilePath = "" 
    datatypeCols = []

    def __init__(self, resourceId, mappingName):
        self.resourceId = resourceId
        self.mappingName = mappingName
        self.init()

    def init(self):
        self._parseMapping()
        self._getCsvPath()
        self._identifyDatatypeCols()

    def _parseMapping(self):
        mappings = Mapping(self.resourceId)
        mappings.init_mappings_only()
        mapping = mappings.get_mapping_by_name(self.mappingName)
        self.csvDelimiter = mapping['delimiter']
        self.headerLine = mapping['header']
        self.csvHeader = mappings.get_header_by_name(self.mappingName)

    def _getCsvPath(self):
        tabularFile = TabularFile(self.resourceId)
        self.csvFilePath = tabularFile.getCsvFilePathDownload()

    def _identifyDatatypeCols(self):
        for headerItem in self.csvHeader[self.mappingName]:
            if(len(headerItem[1].split("^^")) > 1):
                self.datatypeCols.append(headerItem)

    def validate(self):
        pass

    def readCsv(self):

        with open(self.csvFilePath, 'rU') as csvfile:
            csvReader = csv.DictReader(csvfile, delimiter=self.csvDelimiter, quotechar='"')
            for row in csvReader:
                for column in self.datatypeCols:
                    columnIndex = int(column[0]) - 1
                    columnValue = column[1]
                    columnDatatype = columnValue.split("^^")[-1]
                    row[csvReader.fieldnames[columnIndex]] = self.validateValue(columnDatatype, row[csvReader.fieldnames[columnIndex]])
                print ', '.join(row)

            print columnIndex
            print columnValue
            print df.dtypes.index[columnIndex]
            import ipdb; ipdb.set_trace()

    def validateValue(self, datatype, value):
        if(re.search("integer", datatype)):
            print "int"
            print value

        if(re.search("dateTime", datatype)):
            print "dateTime"
            print value


if __name__ == "__main__":
    testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    testMappingName = "csv2rdf-interface-generated-with-datatype"
    v = CsvDatatypeValidator(testResourceId, testMappingName)
    v.readCsv()
    import ipdb; ipdb.set_trace()

