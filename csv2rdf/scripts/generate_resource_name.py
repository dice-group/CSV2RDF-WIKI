#!/home/lodstats/.virtualenvs/thedatahub/bin/python

import sys

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-r", "--resource_uri", dest="resource_uri",
                  help="Resource URI", metavar="RESOURCE_URI")

(options, args) = parser.parse_args()

resource_uri = options.resource_uri

from csv2rdf.ckan.ckanio import CkanIO

io = CkanIO()
full_resource_list = io.get_full_resource_list()
resource_object = {}
for resource in full_resource_list:
    if(resource['url'] == resource_uri):
        resource_object = resource

if(not resource_object):
    sys.exit('')

from csv2rdf.ckan.package import Package
package = Package(resource_object['package_id'])
package_name = package.name

import requests
try:
    r = requests.head(resource_object['url'], timeout=1)
    if(r.status_code == requests.codes.ok):
        filesize_in_mb = str( int(r.headers['content-length']) / (1024*1024) )
    else:
        from random import randrange
        filesize_in_mb = "br"+str(randrange(10))
except BaseException as e:
    from random import randrange
    filesize_in_mb = "br"+str(randrange(10))
    print str(e)

from csv2rdf.ckan.ckanio import queries
q = queries.Queries()
serialization_format = q.detect_format(resource_object['format'])

resource_name = package_name + "." + filesize_in_mb + "." + serialization_format

print resource_name
