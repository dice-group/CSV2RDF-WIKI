import csv2rdf.ckan.ckanio
import csv2rdf.tabular.tabularfile
import csv2rdf.config.config
ckanio = csv2rdf.ckan.ckanio.CkanIO()
for item in ckanio.get_csv_resource_list():
    tf = csv2rdf.tabular.tabularfile.TabularFile(item['id'])
    tf.download()
    tf.get_info_about()
