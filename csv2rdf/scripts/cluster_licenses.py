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
#full_package_list = [{"license_id": "some_id"},
#                     {"license_id": "some_id"},
#                     {"license_id": "some_id3"},
#                     {"license_id": "some_id6"},
#                     {"license_id": "some_id4"},
#                     {"license_id": "some_id"},
#                     {"license_id": "some_id2"}]
licenses = {}
for package_id in package_list: 
    print "Processing " + str(package_id)
    try:
        package = db.loadDbase(package_id)
    except BaseException as e:
        print str(e)
    if( hasattr(package, 'license_url')):
        license_url = package.license_url 
    else:
        license_url = ''
    license_by_id = licenses.get(package.license_id, 0)
    if(license_by_id == 0):
        count = 1
    else:
        count = license_by_id['count'] + 1
    licenses[package.license_id] = {'license_title': package.license_title,
                                    'license': package.license,
                                    'license_url': license_url,
                                    'count': count}

print "Processing complete, saving now"
import cPickle
import datetime
from csv2rdf.config.config import data_path
date_now = str(datetime.datetime.now().strftime("%d%B%Y"))
filename = "licenses_precise"+date_now
filepath = data_path + filename
cPickle.dump(licenses, open(filepath, 'wb'))
print "complete!"
