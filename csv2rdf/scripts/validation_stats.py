import csv2rdf.ckan.ckanio
import csv2rdf.tabular.tabularfile
import csv2rdf.config.config
import logging
ckanio = csv2rdf.ckan.ckanio.CkanIO()
csv_resource_list = ckanio.get_csv_resource_list()
for num, item in enumerate(csv_resource_list):
    if(num < 12342):
        continue
    logging.debug("Resource %d out of %d" % (num, len(csv_resource_list)))
    try:
        tf = csv2rdf.tabular.tabularfile.TabularFile(item['id'])
        tf.download()
        tf.get_info_about()
    except BaseException as e:
        logging.error("Outer error: %s" % str(e))
