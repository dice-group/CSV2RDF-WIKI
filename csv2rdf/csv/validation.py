import re
import csv
import datetime
import logging
import csv2rdf.tabular.tabularfile
import csv2rdf.tabular.mapping

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
        mappings = csv2rdf.tabular.mapping.Mapping(self.resourceId)
        mappings.init_mappings_only()
        mapping = mappings.get_mapping_by_name(self.mappingName)
        self.csvDelimiter = mapping['delimiter']
        self.headerLine = mapping['header']
        self.csvHeader = mappings.get_header_by_name(self.mappingName)

    def _getCsvPath(self):
        tabularFile = csv2rdf.tabular.tabularfile.TabularFile(self.resourceId)
        self.csvFilePath = tabularFile.getCsvFilePathDownload()
        self.csvValidatedFilePath = self.csvFilePath + ".validated"

    def _identifyDatatypeCols(self):
        for headerItem in self.csvHeader[self.mappingName]:
            if(len(headerItem[1].split("^^")) > 1):
                self.datatypeCols.append(headerItem)

    def validate(self):
        with open(self.csvFilePath, 'rb+') as csvfile, open(self.csvValidatedFilePath, 'wb+') as validatedcsvfile:
            csvReader = csv.DictReader([x.replace('\0', '') for x in csvfile], delimiter=self.csvDelimiter, quotechar='"')
            csvWriter = csv.DictWriter(validatedcsvfile, delimiter=self.csvDelimiter, quotechar='"', fieldnames=csvReader.fieldnames)
            for row in csvReader:
                for column in self.datatypeCols:
                    columnIndex = int(column[0]) - 1
                    columnValue = column[1]
                    columnDatatype = columnValue.split("^^")[-1]
                    row[csvReader.fieldnames[columnIndex]] = self.validateValue(columnDatatype, row[csvReader.fieldnames[columnIndex]])
                csvWriter.writerow(row)

        return self.csvValidatedFilePath

    def validateValue(self, datatype, value):
        value = value.strip()
        if(value == ""):
            return ""

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

        #24-Sep-10
        elif(re.match("\d{2}-\w{3}-\d{2}", value)):
            value = value.split("-")
            if(int(value[2]) < 40):
                value[2] = "20%s"%value[2]
                format = "%d-%b-%Y"
            else:
                format = "%d-%b-%y"
            value = "-".join(value)
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
    testResourceId = "daacea8c-789a-4cfd-b685-c927e9adf54c"
    testResourceId = "e8b8eb07-148f-492e-a2a1-95a663644ec5"
    testResourceId = "141cd493-3237-428b-a56b-b88fd5f9da7c"
    testMappingName = "csv2rdf-interface-generated"
    v = CsvDatatypeValidator(testResourceId, testMappingName)
    v.validate()
    import ipdb; ipdb.set_trace()

