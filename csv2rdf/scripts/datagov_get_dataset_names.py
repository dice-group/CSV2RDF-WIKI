from csv2rdf.config import config

import cPickle
f = open(config.data_gov_pages_folder + "datasets", "rb")
dataset_name_list = cPickle.load(f)
f.close()

print dataset_name_list[0]
