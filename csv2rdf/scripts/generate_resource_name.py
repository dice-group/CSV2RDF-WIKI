#!/home/lodstats/.virtualenvs/thedatahub/bin/python

import sys

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-r", "--resource_uri", dest="resource_uri",
                  help="Resource URI", metavar="RESOURCE_URI")

(options, args) = parser.parse_args()

resource_uri = unicode(options.resource_uri, 'utf-8')

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

resource_name = package_name

import requests
try:
    r = requests.head(resource_object['url'], timeout=1)
    if(r.status_code == requests.codes.ok):
        resource_name = resource_name + '.' + str( int(r.headers['content-length']) / (1024*1024) )
except BaseException as e:
    pass

from csv2rdf.ckan.ckanio import queries
q = queries.Queries()
serialization_format = q.detect_format(resource_object['format'])

resource_name = resource_name + "." + serialization_format

print resource_name
