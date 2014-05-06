from csv2rdf.config import config
from bs4 import BeautifulSoup
import re

print config.data_gov_pages_folder

dataset_name_list = []
number_of_pages = 5248
for i in range(1, number_of_pages + 1):
    f = open(config.data_gov_pages_folder + "page" + str(i), "rU")
    page = f.read()
    f.close()
    soup = BeautifulSoup(page)
    for dataset in soup.find_all(href=re.compile("dataset/")):
        dataset_name_list.append(dataset["href"].split("/")[-1])
 
import cPickle
f = open(config.data_gov_pages_folder + "datasets", "wb")
cPickle.dump(dataset_name_list, f)
f.close()
