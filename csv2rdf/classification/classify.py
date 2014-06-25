import re
import foxpy.fox
from csv2rdf.ckan.resource import Resource
from csv2rdf.ckan.package import Package
from csv2rdf.tabular.mapping import Mapping
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.tabular.refine import Refine

class Classificator(object):
    def __init__(self):
        self.fox = foxpy.fox.Fox()

    def concatHeaders(self, headers):
        uniqueHeaders = set()
        for header in headers:
            for item in header[header.keys()[0]]:
                if(not item[1].startswith('http')):
                    uniqueHeaders.add(item[1])
        concatHeaders = ""
        for item in uniqueHeaders:
            concatHeaders += item + " "
        return concatHeaders

    def concatTable(self, table):
        concatTable = ""
        for col in table['columns'][1:]: #remove header
            colContent = ""
            for item in col['content']:
                colContent += str(item) + " "
            numbers = len(re.findall("[0-9]", colContent))
            stringLength = len(colContent)
            if(float(numbers)/stringLength < 0.4):
                concatTable += colContent

        if(concatTable == ''):
            concatTable = 'no strings in the table'
        return concatTable

    def getResourceMetadata(self, resourceId):
        resource = Resource(resourceId)
        resource.init()
        
        mapping = Mapping(resourceId)
        headers = mapping.get_mapping_headers()
        headers = self.concatHeaders(headers)

        tf = TabularFile(resourceId)
        csvDataframe = tf.get_csv_data()
        refine = Refine(resourceId)
        table = refine.structure_by_cols(csvDataframe)
        table = self.concatTable(table)

        package = Package(resource.package_name)
        return (resource, package, headers, table)

    def classify(self, text):
        (text, output, log) = self.fox.recognizeText(text)
        return (text, output, log)

    def classifyResource(self, resourceId):
        classified = []
        (resource, package, headers, table) = self.getResourceMetadata(resourceId)
        itemsToClassify = [
                    'resource.description',
                    'package.author',
                    'package.notes',
                    'package.tags',
                    'package.title',
                    'package.extras',
                    'headers',
                    'table'
                ]
        for item in itemsToClassify:
            stringToClassify = eval(item)
            if type(stringToClassify) is list:
                stringToClassify = ' '.join(stringToClassify)
            elif type(stringToClassify) is dict:
                tmp = ""
                for key in stringToClassify.keys():
                    tmp += key + " " + stringToClassify[key] + "\n"
                stringToClassify = tmp
            
            classified.append({item: self.fox.recognizeText(stringToClassify)})
        return classified

if __name__ == "__main__":
    testResourceId = "8b51874e-cda8-4910-a3c0-9140e11164a3"
    classificator = Classificator()
    print classificator.classifyResource(testResourceId)
