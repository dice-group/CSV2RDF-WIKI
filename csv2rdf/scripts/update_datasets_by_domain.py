class Tags(object):
    tags = {}

    def add(self, tag):
        if(tag in self.tags.keys()):
            self.tags[tag] += 1
        else:
            self.tags[tag] = 1


from csv2rdf.ckan.ckanio import CkanIO
from csv2rdf.ckan.package import Package

ckanio = CkanIO()
csv_resource_list = ckanio.get_csv_resource_list()
print "Loaded resource list"

tags = Tags()

list_size = len(csv_resource_list)

for num, resource in enumerate(csv_resource_list): 
    print("%d out of %d" %(num, list_size))
    package_id = resource['package_id']
    package = Package(package_id)
    for tag in package.tags:
        tags.add(tag)
    #print package.extras

#print tags.tags

#print "Processing complete, saving now"
import cPickle
#import datetime
from csv2rdf.config.config import data_path
#date_now = str(datetime.datetime.now().strftime("%d%B%Y"))
filename = "tags"
filepath = data_path + filename
cPickle.dump(tags.tags, open(filepath, 'wb'))
print "complete!"
