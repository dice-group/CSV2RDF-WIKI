from csv2rdf.ckan.ckanio import CkanIO
ckanio = CkanIO()
full_package_list = ckanio.get_full_package_list()
#full_package_list = [{"license_id": "some_id"},
#                     {"license_id": "some_id"},
#                     {"license_id": "some_id3"},
#                     {"license_id": "some_id6"},
#                     {"license_id": "some_id4"},
#                     {"license_id": "some_id"},
#                     {"license_id": "some_id2"}]
licenses = {}
for package in full_package_list:
    licenses[package.license_id] = licenses.get(package.license_id, 0) + 1

import cPickle
import datetime
from csv2rdf.config.config import data_path
date_now = str(datetime.datetime.now().strftime("%d%B%Y"))
filename = "licenses_precise"+date_now
filepath = data_path + filename
cPickle.dump(licenses, open(filepath, 'wb'))
