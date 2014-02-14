import json
import numpy

from csv2rdf.tabular.mapping import Mapping
from csv2rdf.tabular.tabularfile import TabularFile


class Refine(object):
    def __init__(self, resource_id):
        self.resource_id = resource_id
        pass

    def get_mappings(self):
        resource_id = self.resource_id

        #get the mappings from wiki page
        mapping = Mapping(resource_id)
        mapping.init()
        return mapping.mappings

    def get_csv_table(self):
        resource_id = self.resource_id
        table = {}
        table['columns'] = []

        #first 20 lines of the csv file
        tf = TabularFile(resource_id)
        csv_obj = tf.get_csv_data()
        for column in csv_obj.columns:
            table_column = {}
            table_column['name'] = column
            table_column['content'] = []
            for item in csv_obj[column]:
                if(not isinstance(item, str)):
                    item = numpy.asscalar(item)
                table_column['content'].append(item)
            table['columns'].append(table_column);
        return table

    def pack_csv_mappings_in_json(self):
        mappings = self.get_mappings()
        csv_table = self.get_csv_table()
        json_dump = {
                     "mappings": mappings,
                     "csv": csv_table
                    }
        return json.dumps(json_dump)

if __name__ == "__main__":
    refine = Refine("0e8012f2-fdbb-4a88-ab11-5d8b012b06a2")
    print refine.pack_csv_mappings_in_json()
