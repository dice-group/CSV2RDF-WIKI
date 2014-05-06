import cPickle
from csv2rdf.config.config import data_path
filename = "licenses_precise06May2014"
filepath = data_path + filename
licenses = cPickle.load(open(filepath, 'rb'))
for license in licenses:
    arr = [str(license), str(licenses[license]['count']), str(licenses[license]['license_title']), str(licenses[license]['license_url']), str(licenses[license]['license'])]
    print ", ".join(arr)
