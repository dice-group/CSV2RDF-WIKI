from ckan.application import CkanApplication

ckan_app = CkanApplication()

ckan_app.update_full_package_list()
#ckan_app.update_full_resource_list()
#ckan_app.update_all_rdf_resources()
#ckan_app.update_csv_resource_list()

# update the soft links in the sparqlified_exposed folder
#ckan_app.update_sparqlified_list()
# update get_exposed_rdf_list (used by publicdata.eu CKAN instance)
# require: update_sparqlified_list()
#ckan_app.update_exposed_rdf_list()
