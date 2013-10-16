import csv2rdf.ckan.ckanio
import csv2rdf.tabular.tabularfile
import csv2rdf.config.config
import optparse
import sys
import pprint

parser = optparse.OptionParser()
parser.add_option("-r", "--resource", dest="resource",
                  help="resource to lookup", metavar="RES")

(options, args) = parser.parse_args()

if(options.resource is None):
    sys.exit("Specify -r RESOURCE_NUMBER")

ckanio = csv2rdf.ckan.ckanio.CkanIO()
csv_resource_list = ckanio.get_csv_resource_list()
resource = csv_resource_list[int(options.resource)]

pprinter = pprint.PrettyPrinter()
pprinter.pprint(resource)
