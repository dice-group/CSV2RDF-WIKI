import requests
import time
from csv2rdf.config import config

print config.data_gov_pages_folder

number_of_pages = 5248

for i in range(1, number_of_pages + 1):
    r = requests.get("http://catalog.data.gov/dataset?page="+str(i))
    #print r.status_code
    assert r.status_code == requests.status_codes.codes.OK
    f = open(config.data_gov_pages_folder + "page" + str(i), "w")
    f.write(r.content)
    f.close()
    time.sleep(0.5)
