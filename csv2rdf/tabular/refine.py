import json
import numpy

from csv2rdf.tabular.mapping import Mapping
from csv2rdf.tabular.tabularfile import TabularFile
from csv2rdf.ckan.resource import Resource


class Refine(object):
    def __init__(self, resource_id):
        self.resource_id = resource_id

    def get_mappings(self):
        resource_id = self.resource_id

        #get the mappings from wiki page
        mapping = Mapping(resource_id)
        mapping.init()
        return mapping.mappings

    def get_mappings_json(self):
        mappings = self.get_mappings()
        return json.dumps(mappings, ensure_ascii=False)

    def get_csv_table(self):
        resource_id = self.resource_id

        #first 20 lines of the csv file
        tf = TabularFile(resource_id)
        csv_obj = tf.get_csv_data()
        csv_obj = csv_obj.fillna(0)
        return self.structure_by_rows(csv_obj)

    def get_csv_table_json(self):
        table = self.get_csv_table()
        return json.dumps(table, ensure_ascii=False)

    def structure_by_cols(self, dataframe):
        table = {}
        table['columns'] = []
        for column in dataframe.columns:
            table_column = {}
            table_column['name'] = column
            table_column['content'] = []
            for item in dataframe[column]:
                if(not isinstance(item, str)):
                    item = numpy.asscalar(item)
                table_column['content'].append(item)
            table['columns'].append(table_column);
        return table

    def structure_by_rows(self, dataframe):
        table = {}
        table['rows'] = []
        table['header'] = []
        for column in dataframe.columns:
            header = {}
            header['label'] = column
            header['uri'] = ''
            table['header'].append(header)
        datamatrix = dataframe.as_matrix()
        for row in datamatrix:
            row_to_append = []
            for item in row:
                row_item = {}
                row_item['label'] = item
                row_item['uri'] = ''
                row_to_append.append(row_item)
            table['rows'].append(row_to_append)

        return table

    def get_data_json(self):
        mappings = self.get_mappings()
        csv_table = self.get_csv_table()
        resource = self.get_resource_json()
        resource = json.loads(resource)
        json_dump = {}
        #json_dump["resource"] = resource
        #json_dump["table"] = UTF8Dict(csv_table)
        #json_dump["mappings"] = mappings
        #import ipdb; ipdb.set_trace()
        return json.dumps(json_dump)

    def get_resource(self):
        resource = Resource(self.resource_id)
        resource.init()
        return resource

    def get_resource_json(self):
        resource = self.get_resource()
        return resource.to_JSON()

if __name__ == "__main__":
    #refine = Refine("0e8012f2-fdbb-4a88-ab11-5d8b012b06a2")
    #refine = Refine("13fd759b-549c-44dd-83a2-684e7a0b0147")
    refine = Refine("1695fd9e-0b56-4bbd-a178-f60c76f8014a")
    #print refine.pack_csv_mappings_in_json()
    print refine.get_data_json()
