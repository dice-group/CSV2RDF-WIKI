#from csv2rdf.ckan.ckanio import CkanIO
import csv2rdf.config.config
import csv2rdf.database
from os import listdir
from os.path import isfile, join

#ckanio = CkanIO()
#full_package_list = ckanio.get_full_package_list()
formats_pdeu = eval("""[u'api/sparql', u'n-triple', u'bz2:nt', u'example/rdfa', u'sparql', u'sparql web form', u'ttl', u'application/rdf xml', u'turtle', u'text/turtle', u'html+rdfa', u'rdf/xml, marcxml', u"'application/rdf xml'", u'rdf/turtle', u'n-triples', u'linked data api, rdf json', u'application/rdf+xml', u'text/ntriples', u'rdfa', u'owl', u'RDF', u'example/rdf+xml', u'meta/void', u'skos rdf', u'n3']""")
formats_datahubio = eval("""[u'data file in excel and rdf', u'html+rdfa ', u'void', u'meta/void', u'rdf endpoint', u'api/sparql', u'application/x-ntriples', u'mapping/<owl>', u'rdf, nt', u'ttl:e1:csv', u'gzip:ntriples', u'meta/rdf-schema ', u'api/sparql ', u'html, rdf', u'gz:ttl:owl', u'nt:transparency-international-corruption-perceptions-index', u'example/owl', u'example/ntriples', u'example/rdf xml', u'bz2:nt', u'api/linked-data', u'example/rdfa', u'sparql', u'rdf, sparql+xml', u'example/rdf+json', u'example/rdf+json ', u'ttl', u'xhtml+rdfa', u'application/x-nquads', u'xml, rdf+xml, turtle and json', u'example/n3', u'example/turtle', u'rdf/n3', u'rdf/xml, html, json', u'application/rdf xml', u'turtle', u'text/turtle', u'text/n3', u'mapping/rdfs', u'html+rdfa', u'example/x-turtle', u'rdf+xml ', u'rdf, csv, xml', u'rdf/nt', u'compressed tarfile containing n-triples', u'rdf-n3', u'rdf/turtle', u'rdf (gzipped)', u'example/n3 ', u'sparql-xml', u'7z:ttl', u'text/rdf+n3', u'n-triples', u'gz:nt', u'gz:nq', u'application/rdf+json', u'application/rdfs', u'ttl.bzip2', u'rdf-turtle', u'gz:ttl', u'example/html+rdfa', u'meta/rdf-schema', u'example/rdf+xml', u'mapping/d2r', u'application/rdf+xml ', u'application/rdf+xml', u'meta/rdf+schema', u'text/ntriples', u'rdf-xml', u'gzip::nquads', u'application/x-turtle', u'meta/void\t', u'nt:meta', u'api/dcat', u'rdfa', u'ontology', u'example/rdf+n3', u'rdf+xml', u'application/turtle', u'application/n-triples', u'html, rdf, dcif', u'rdf, owl', u'RDF', u'application/ld+json', u'json-ld', u'example/rdf+ttl', u'xhtml, rdf/xml, turtle', u'nt', u'rdf:products:org:openfoodfacts', u'sparql-json', u'rdf/xml, turtle, html', u'mapping/owl', u'n3']""")
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
