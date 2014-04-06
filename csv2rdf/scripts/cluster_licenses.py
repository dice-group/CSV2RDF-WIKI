from csv2rdf.ckan.ckanio import CkanIO

ckanio = CkanIO()
full_package_list = ckanio.get_full_package_list()
print "Loaded package list"
#full_package_list = [{"license_id": "some_id"},
#                     {"license_id": "some_id"},
#                     {"license_id": "some_id3"},
#                     {"license_id": "some_id6"},
#                     {"license_id": "some_id4"},
#                     {"license_id": "some_id"},
#                     {"license_id": "some_id2"}]
licenses = {}
for package in full_package_list: 
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
