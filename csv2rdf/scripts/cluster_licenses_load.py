import cPickle
from csv2rdf.config.config import data_path
filename = "licenses_precise04May2014"
filepath = data_path + filename
licenses = cPickle.load(open(filepath, 'rb'))
print licenses
