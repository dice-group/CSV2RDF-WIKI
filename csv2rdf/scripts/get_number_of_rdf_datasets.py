#from csv2rdf.ckan.ckanio import CkanIO
import csv2rdf.config.config
import csv2rdf.database
from os import listdir
from os.path import isfile, join

#ckanio = CkanIO()
#full_package_list = ckanio.get_full_package_list()
data_packages_path = csv2rdf.config.config.data_packages_path
package_list = [f for f in listdir(data_packages_path) if isfile(join(data_packages_path, f)) ]
db = csv2rdf.database.DatabasePlainFiles(data_packages_path)
print "Loaded package list"
formats = set()
mimetypes = set()
count = 0
for package_id in package_list: 
    #print "Processing " + str(package_id)
    try:
        package = db.loadDbase(package_id)
        for res in package.resources:
            if(res['format'] == "RDF" or
               res['format'] == "application/xml+rdf" or
               res['format'] == "application/rdf+xml"):
                count += 1
                break
            #formats.add(res['format'])
            #mimetypes.add(res['mimetype'])
        #print package.resources[0]['mimetype']
    except BaseException as e:
        print str(e)

print count
#print formats
#print mimetypes

print "Processing complete, saving now"
print "complete!"
