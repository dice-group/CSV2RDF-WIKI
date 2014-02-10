import os
import pandas
import numpy

from csv2rdf.tabular.mapping import Mapping

def convert_to_zero_index(list_one_index):
    list_zero_index = []
    for item in list_one_index:
        list_zero_index.append(item - 1)
    return list_zero_index

#pick random csv file from csv directory
csv_dir = "/home/akswadmin/dumps/csv/"

for num, resource_id in enumerate(os.listdir(csv_dir)):
    if(num < 20):

        mapping = Mapping(resource_id=resource_id)
        wikipage_exists = mapping.init_mappings_only()
        if(wikipage_exists):
            m = mapping.get_mapping_by_name('default-tranformation-configuration')
            #header - int row numbers to use as the column names - can be a list [0,1,4]
            #header = convert_to_zero_index(m['header'])
            #skiprows - row numbers to skip - list 0 indexed
            skiprows = convert_to_zero_index(m['omitRows'])
            #sep - separator
            sep = m['delimiter']
        else:
            sep = ","
            skiprows = None
            print "Wiki page does not exist"
            continue

        csv_obj = pandas.read_csv(csv_dir+resource_id, 
                                  #header=header,
                                  #index_col=False,
                                  skiprows=skiprows,
                                  sep=sep,
                                  nrows=20, 
                                  error_bad_lines=False)
        cells_float = []
        cells_float_ratio = []
        for (index, row) in csv_obj.iterrows(): 
            #import ipdb; ipdb.set_trace()
            cells_float.append(0)
            for cell in row:
                if((isinstance(cell, float) or isinstance(cell, int)) and not numpy.isnan(cell)):
                    cells_float[-1] += 1
            cells_float_ratio.append(float(cells_float[-1])/len(row))
        cells_float_ratio_average = sum(cells_float_ratio) / len(cells_float_ratio)
        print cells_float_ratio_average
        if(cells_float_ratio_average > 0.45):
            print csv_dir+resource_id
            print num
    else:
        break


