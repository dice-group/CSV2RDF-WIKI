#from csv2rdf.ckan.ckanio import CkanIO
import csv2rdf.config.config
import csv2rdf.database
from os import listdir
from os.path import isfile, join

#ckanio = CkanIO()
#full_package_list = ckanio.get_full_package_list()
formats_pdeu = eval("""[u'api/sparql', u'n-triple', u'bz2:nt', u'example/rdfa', u'sparql', u'sparql web form', u'ttl', u'application/rdf xml', u'turtle', u'text/turtle', u'html+rdfa', u'rdf/xml, marcxml', u"'application/rdf xml'", u'rdf/turtle', u'n-triples', u'linked data api, rdf json', u'application/rdf+xml', u'text/ntriples', u'rdfa', u'owl', u'RDF', u'example/rdf+xml', u'meta/void', u'skos rdf', u'n3']""")
data_packages_path = csv2rdf.config.config.data_packages_path
package_list = [f for f in listdir(data_packages_path) if isfile(join(data_packages_path, f)) ]
db = csv2rdf.database.DatabasePlainFiles(data_packages_path)
print "Loaded package list"
#formats = set()
#mimetypes = set()
count = 0
for package_id in package_list: 
    #print "Processing " + str(package_id)
    try:
        package = db.loadDbase(package_id)
        for res in package.resources:
            if(res['format'] in formats_pdeu):
            #   res['format'] == "application/xml+rdf" or
            #   res['format'] == "application/rdf+xml"):
                count += 1
                break
            #formats.add(res['format'])
            #mimetypes.add(res['mimetype'])
        #print package.resources[0]['mimetype']
    except BaseException as e:
        print str(e)

print count

print "Processing complete, saving now"
print "complete!"
