import dbpediao.ontology
import re

from SPARQLWrapper import SPARQLWrapper, JSON
from csv2rdf.ckan.resource import Resource
from csv2rdf.ckan.package import Package
from csv2rdf.tabular.mapping import Mapping
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.tabular.refine import Refine

class ClassifierInterface(object):
    def __init__(self):
        self.dbpediao = dbpediao.ontology.OntologyReasoner()

    def _recognizeEntitiesResource(self, resourceId):
        """
            Get the structure elements of the resource
            Use recognizeEntities function to recognizeEntities all of them
        """
        classified = []
        (resource, package, headers, table) = self._getResourceMetadata(resourceId)
        itemsToClassify = [
                    'resource.description',
                    'package.author',
                    'package.notes',
                    'package.tags',
                    'package.title',
                    'package.extras',
                    #TODO: filename
                    #'headers',
                    #'table'
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
                classifiedOne = self._recognizeEntities(stringToClassify)
                classified.append({item: classifiedOne})
            except BaseException as e:
                print str(e)
        return classified

    def _getClassesForEntities(self, entities):
        sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        classes = {}
        for entity in entities:
            sparql.setQuery("""
                SELECT ?type
                WHERE { <%s> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> ?type . }
            """ % entity[1])
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            classes[entity] = set()
            for result in results['results']['bindings']:
                if(result['type']['value'].startswith('http://dbpedia.org/ontology')):
                    classes[entity].add(result['type']['value'])
            classes[entity] = self.dbpediao.findBottomConcept(classes[entity])
        return classes

    def getEntitiesWithClasses(self, resourceId):
        entities = set(self.getEntities(resourceId))
        #consider only dbpedia entities
        dbpediaEntities = [x for x in entities if x[1].startswith('http://dbpedia')]
        classes = self._getClassesForEntities(dbpediaEntities)
        return classes
