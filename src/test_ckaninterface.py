import unittest
from urlparse import urlparse
from ckaninterface import Resource

class FindTest (unittest.TestCase):
  def setUp (self):
    self.testid = '2409b9b4-3261-4543-9653-ffd28222b745'
    
  def tearDown (self):
    pass
  
  #
  # CKAN tests
  #
      
  def test_01_load_from_ckan (self):
    """ 1: Test load_from_ckan method from Resource class 
        Check if attributes of the Resource object fetched from CKAN exist:
        -- revision_id - used for fetching package_id
        -- url - used for downloading the data file """
    resource = Resource(self.testid)
    object = resource.load_from_ckan()
    self.failUnless('url' in object, 'Tested object has no url attribute.')
    self.failUnless('revision_id' in object, 'Tested object has no revision_id attribute.')
    
  def test_02_request_package_name(self):
    """ 2: Test request_package_name method from Resource class
        Check if returns a value, which is not NULL """
    resource = Resource(self.testid)
    resource.unpack_object_to_self(resource.load_from_ckan())
    package_name = resource.request_package_name()
    self.failUnless(package_name, 'package name is NULL!')
    
  def test_03_get_ckan_url(self):
    """ 3: Test if get_ckan_url method from Resource class
        returns URI string """
    resource = Resource(self.testid)
    resource.unpack_object_to_self(resource.load_from_ckan())
    resource.package_name = resource.request_package_name()

    parsed_url = urlparse(resource.get_ckan_url()) # returns ParseResult class instance    
    self.failUnless(parsed_url.scheme, "Scheme is missing.")
    self.failUnless(parsed_url.netloc, "Net Location (e.g. publicdata.eu) is missing.")
    self.failUnless(parsed_url.path, "Path is missing.")
  
  #
  # Wiki tests
  #
    
  def test_04_get_wiki_url(self):
    """ 4: Test if get_wiki_url method from Resource class
        returns URI string.
        The result depends on config.py file."""
    resource = Resource(self.testid)
    
    parsed_url = urlparse(resource.get_wiki_url())
    self.failUnless(parsed_url.scheme, "Scheme is missing.")
    self.failUnless(parsed_url.netloc, "Net Location (e.g. publicdata.eu) is missing.")
    self.failUnless(parsed_url.path, "Path is missing.")
    
  def test_05_check_wiki_login(self):
    """ 5: Test if wiki is accessible and can login.
        Login credentials are in config.py """
    import wikitools
    import config
    wiki_site = wikitools.Wiki(config.wiki_api_url)
    login = wiki_site.login(config.wiki_username, password=config.wiki_password)
    self.failUnless(login, "Can't login to the MediaWiki instance!")
    
  def test_06_request_wiki_page(self):
    """ 6: Test if wiki page for this Resource exists """
    import wikitools
    import config
    resource = Resource(self.testid)
    resource.wiki_site = wikitools.Wiki(config.wiki_api_url)
    resource.wiki_site.login(config.wiki_username, password=config.wiki_password)
        
    wiki_page = resource._request_wiki_page()
    self.failUnless(wiki_page, "Wiki page does not exist or empty!")
  
  def test_07_extract_csv_configurations(self):
    """ 7: Test the parser for CSV configurations on Wiki page """
    import wikitools
    import config
    resource = Resource(self.testid)
    resource.wiki_site = wikitools.Wiki(config.wiki_api_url)
    resource.wiki_site.login(config.wiki_username, password=config.wiki_password)
        
    wiki_page = resource._request_wiki_page()
    mappings = resource._extract_csv_mappings(wiki_page)
    for mapping in mappings:
      self.failUnless(mapping['type'] == 'RelCSV2RDF', 'Wrong mapping type, should be RelCSV2RDF.')
      self.failUnless(mapping['name'], 'Name of mapping is undefined!')
      self.failUnless(mapping['header'], 'Header line is not specified')
      self.failUnless(mapping['omitCols'], 'omitCols is not specified')
      self.failUnless(mapping['omitRows'], 'omitRows is not specified')
    
  def test_08_load_mapping(self):
    """ 8: Test fetching the wiki page and parsing together """
    import wikitools
    import config
    resource = Resource(self.testid)
    resource.wiki_site = wikitools.Wiki(config.wiki_api_url)
    resource.wiki_site.login(config.wiki_username, password=config.wiki_password)
    
    mappings = resource.load_mappings()
    self.failUnless(mappings, 'No mappings exists!')
  
  #
  # Download tests
  #
  
  def test_09_download(self):
    """ Download resource and check if downloaded file is not empty """
    pass
  
  def test_10_read_resource_file(self):
    pass
  
  def 
  
if __name__ == '__main__':
   unittest.main()