import re
import json
import foxpy.fox
import spotlight
from csv2rdf.ckan.resource import Resource
from csv2rdf.ckan.package import Package
from csv2rdf.tabular.mapping import Mapping
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.tabular.refine import Refine

class Classificator(object):
    def __init__(self, foxlight=4):
        self.fox = foxpy.fox.Fox(foxlight) #foxlight stands for NER method, see Fox class for details

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

    def classifyFox(self, text):
        (text, output, log) = self.fox.recognizeText(text)
        return (text, output, log)

    def classifySpotlight(self, text):
        annotationServiceUri = 'http://spotlight.dbpedia.org/rest/annotate'
        confidence = 0.5
        support = 20
        return spotlight.annotate(annotationServiceUri, text, confidence=confidence, support=support)

    def getEntitiesSpotlight(self, resourceId):
        spotlight = self.classifyResource(resourceId, classifierName="Spotlight")
        entitiesRecognized = set()
        for structuralElement in spotlight:
            structuralElementName = structuralElement.keys()[0]
            entities = structuralElement[structuralElementName]
            for entity in entities:
                entitiesRecognized.add(entity['URI'])
        return entitiesRecognized

    def getEntitiesFox(self, resourceId):
        fox = classificator.classifyResource(resourceId, classifierName="Fox")
        entitiesRecognized = set()
        for structuralElement in fox:
            structuralElementName = structuralElement.keys()[0]
            (text, entities, log) = structuralElement[structuralElementName]
            entities = json.loads(entities)
            if( '@graph' in entities ):
                for entity in entities['@graph']:
                    entitiesRecognized.add(entity['means'])
        return entitiesRecognized

    def getEntities(self, resourceId):
        spotlightEntities = self.getEntitiesSpotlight(resourceId)
        foxEntities = self.getEntitiesFox(resourceId)
        import ipdb; ipdb.set_trace()

    def classifyResource(self, resourceId, classifierName='Fox'):
        classifier = eval('self.classify'+classifierName)
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
            
            try:
                classified.append({item: classifier(stringToClassify)})
            except BaseException as e:
                print str(e)
        return classified

if __name__ == "__main__":
    testResourceId = "8b51874e-cda8-4910-a3c0-9140e11164a3"
    classificator = Classificator()
    entities = classificator.getEntities(testResourceId)
