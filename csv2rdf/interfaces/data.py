import re

from csv2rdf.ckan.package import Package
from csv2rdf.ckan.resource import Resource
from csv2rdf.tabular.mapping import Mapping
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.tabular.refine import Refine

class DataInterface(object):
    def __init__(self):
        pass

    def _concatHeaders(self, headers):
        uniqueHeaders = set()
        for header in headers:
            for item in header[header.keys()[0]]:
                if(not item[1].startswith('http')):
                    uniqueHeaders.add(item[1])
        concatHeaders = ""
        for item in uniqueHeaders:
            concatHeaders += item + " "
        return concatHeaders

    def _concatTable(self, table):
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

    def _getResourceMetadata(self, resourceId):
        resource = Resource(resourceId)
        resource.init()
        
        mapping = Mapping(resourceId)
        headers = mapping.get_mapping_headers()
        headers = self._concatHeaders(headers)

        tf = TabularFile(resourceId)
        csvDataframe = tf.get_csv_data()
        refine = Refine(resourceId)
        table = refine.structure_by_cols(csvDataframe)
        table = self._concatTable(table)

        package = Package(resource.package_name)
        return (resource, package, headers, table)

    def _getFilePath(self, resourceId):
        tf = TabularFile(resourceId)
        return tf.get_csv_file_path()

    def _getMappings(self, resourceId):
        mapping = Mapping(resourceId)
        return mapping

    def _getOriginalHeader(self, resourceId):
        refine = Refine(resourceId)
        return refine.get_csv_table()['header']

