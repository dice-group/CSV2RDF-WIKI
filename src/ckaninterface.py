from ckanclient import CkanClient
import wikitools
from database import Database
import os
from unidecode import unidecode
import re
import urllib2
from prefixcc import PrefixCC
import subprocess
import json
import requests
requests.defaults.danger_mode = True
import time
import csv
import urllib
import magic

#Configs
import config

# 
# For execution time measure:
# import time
# start_time = time.time()
# function()
# print time.time() - start_time, "seconds"
# 
            
if __name__ == '__main__':
    #ckan = CKAN_Application()
    #ckan.get_sparqlified_list()
    #Test area				
    #getting package list
    #ckan = CkanInterface(base_location='http://publicdata.eu/api', api_key='e7a928be-a3e8-4a34-b25e-ef641045bbaf')
    #package_list = ckan.getPackageList()
    #print ckan.getEntity("staff-organograms-and-pay-joint-nature-conservation-committee")
    #package_id
    
    #wiki_text = resource.generate_default_wiki_page()
    #resource.create_wiki_page(wiki_text)
    #(sparqlify_message, return_code) = resource.transform_to_rdf('default-tranformation-configuration')
    #print sparqlify_message
    #print resource.get_ckan_url()
    
    #print resource.get_sparqlify_configuration_url('default-tranformation-configuration')
    #print resource.get_rdf_file_url('default-tranformation-configuration')
    #print resource.filename
    #print resource.get_csv_file_path()
    #print resource.get_csv_file_url()
    #print resource.get_wiki_url()
    #print resource.generate_default_wiki_page()
    #configs = resource.extract_csv_configurations()
    #print resource._convert_csv_config_to_sparqlifyml(configs[1])
    #print resource.get_sparqlify_configuration_path('default-tranformation-configuration')
    #package = Package(resource.package_name)
    #print package.resources
    #package.download_all_resources()
    
    #print ckan.createDefaultPageForAllCSV()
    
    #create a list of csv resources (?)
    #ckan.updateCSVResourceList()
    #csvResources = ckan.getCSVResourceList()
    #print len(csvResources)
    #CSV: 12224
    #Overall: 55846
    
    #print resource.transform_to_rdf('default-tranformation-configuration')
    