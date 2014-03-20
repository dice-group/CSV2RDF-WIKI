import requests
import json
from csv2rdf.config.config import ckan_api_url

r = requests.get(ckan_api_url + "/rest/licenses")
assert r.status_code, requests.codes.ok
licenses = json.loads(r.content)
for num, license in enumerate(licenses):
    print license['title'], license['url'], license['is_okd_compliant'], license['is_osi_compliant'], license['is_generic']

#Save licenses to file with current datestamp
import cPickle
import datetime
from csv2rdf.config.config import data_path

date_now = str(datetime.datetime.now().strftime("%d%B%Y"))
filename = "licenses"+date_now
filepath = data_path + filename
cPickle.dump(licenses, open(filepath, 'wb'))
