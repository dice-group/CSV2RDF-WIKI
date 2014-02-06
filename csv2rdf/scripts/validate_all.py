import csv2rdf.ckan.ckanio
import csv2rdf.tabular.tabularfile
import csv2rdf.config.config
import logging
tf = csv2rdf.tabular.tabularfile.TabularFile('')
csv_resource_list = tf.get_csv_resource_list_local()
for num, item in enumerate(csv_resource_list):
    logging.debug("Validation resource %d out of %d" % (num, len(csv_resource_list)))
    try:
        tf = csv2rdf.tabular.tabularfile.TabularFile(item)
        tf.validate()
    except BaseException as e:
        logging.error("Outer error: %s" % str(e))
