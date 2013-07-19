from ckan.resource import Resource
from ckan.package import Package

f = open('csv.bigfiles', 'rU')
for line in f.readlines():
    (resource_size, filename) = line.split()
    kbtomb_ratio = 0.0009765625
    resource_size = float(resource_size)*kbtomb_ratio
    resource_id = filename[2:]
    resource = Resource(resource_id)
    resource.init()
    package = Package(resource.package_name)
    link_title = "Dataset resource " + resource.description + " from dataset " + package.title
    link = "* [[Csv2rdf:"+resource_id+"|"+link_title+" (%.2f MB)]]" % resource_size
    print link

