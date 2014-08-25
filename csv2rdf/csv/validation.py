import re
import csv
import datetime
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.tabular.mapping import Mapping

class CsvDatatypeValidator(object):
    csvDelimiter = ""
    headerLine = 0 
    csvHeader = []
    csvFilePath = "" 
    csvValidatedFilePath = "" 
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
        self.csvValidatedFilePath = self.csvFilePath + ".validated"

    def _identifyDatatypeCols(self):
        for headerItem in self.csvHeader[self.mappingName]:
            if(len(headerItem[1].split("^^")) > 1):
                self.datatypeCols.append(headerItem)

    def validate(self):
        with open(self.csvFilePath, 'rb') as csvfile, open(self.csvValidatedFilePath, 'wb+') as validatedcsvfile:
            csvReader = csv.DictReader(csvfile, delimiter=self.csvDelimiter, quotechar='"')
            csvWriter = csv.DictWriter(validatedcsvfile, delimiter=self.csvDelimiter, quotechar='"', fieldnames=csvReader.fieldnames)
            try:
                for row in csvReader:
                    for column in self.datatypeCols:
                        columnIndex = int(column[0]) - 1
                        columnValue = column[1]
                        columnDatatype = columnValue.split("^^")[-1]
                        row[csvReader.fieldnames[columnIndex]] = self.validateValue(columnDatatype, row[csvReader.fieldnames[columnIndex]])
                    csvWriter.writerow(row)
            except BaseException as e:
                import ipdb; ipdb.set_trace()

        return self.csvValidatedFilePath

    def validateValue(self, datatype, value):
        value = value.strip()
        if(re.search("integer", datatype)):
            return self.validateInteger(value)

        if(re.search("float", datatype)):
            return self.validateFloat(value)

        if(re.search("dateTime", datatype)):
            return self.validateDatetime(value)

    def validateDatetime(self, value):
        #30/09/2010
        if(re.match("\d{2}\/\d{2}/\d{4}", value)):
            format = "%d/%m/%Y"
            value = datetime.datetime.strptime(value, format)

        #24-Sep-2010
        elif(re.match("\d{2}-\w{3}-\d{4}", value)):
            format = "%d-%b-%Y"
            value = datetime.datetime.strptime(value, format)

        return value.isoformat()

    def validateFloat(self, value):
        #243.91
        if(re.match("-*\d+\.\d+", value)):
            value = float(value)
        #70,243.91
        #1,673,097.00
        elif(re.match("-*\d+,\d+\.\d+", value) or
             re.match("-*\d+,\d+,\d+.\d+", value)):
            value = "".join(value.split(","))
            value = float(value)

        return value

if __name__ == "__main__":
    testResourceId = "02f31d80-40cc-496d-ad79-2cf02daa5675"
    testMappingName = "csv2rdf-interface-generated-with-datatype"
    v = CsvDatatypeValidator(testResourceId, testMappingName)
    v.readCsv()
    import ipdb; ipdb.set_trace()

