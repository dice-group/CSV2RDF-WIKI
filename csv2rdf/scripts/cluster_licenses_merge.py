#Script specific for csv2rdf.aksw.org portal

licenses = {}

import cPickle
pdeu_licenses = "/home/akswadmin/www/csv2rdf-server/src/CSV2RDF-WIKI/data/licenses_precise21March2014"
licenses_pdeu = cPickle.load(open(pdeu_licenses, 'rU'))

for license in licenses_pdeu:
    licenses[license] = licenses_pdeu[license]

datahub_licenses = "/home/akswadmin/www/csv2rdf-datahubio/src/CSV2RDF-WIKI/data/licenses_precise21March2014"
licenses_dh = cPickle.load(open(datahub_licenses, 'rU'))

for license in licenses_dh:
    #lookup
    if(license in licenses.keys()):
        licenses[license]['count'] += licenses_dh[license]['count']
    else:
        licenses[license] = licenses_dh[license]

#restructure for csv export
csv_licenses = [['id', 'count', 'title', 'url', 'alt_title']]
for license in licenses:
    lic = [unicode(license).encode('utf-8')]
    for prop in licenses[license]:
        lic.append(unicode(licenses[license][prop]).encode('utf-8'))
    csv_licenses.append(lic)

import csv
with open('licenses.csv', 'w') as fp:
    a = csv.writer(fp, delimiter=',')
    a.writerows(csv_licenses)
