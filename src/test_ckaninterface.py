import unittest
from urlparse import urlparse
from ckaninterface import Resource

class FindTest (unittest.TestCase):
  def setUp (self):
    self.testid = '2409b9b4-3261-4543-9653-ffd28222b745'
    
  def tearDown (self):
    pass
      
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
        
    pass
  
if __name__ == '__main__':
   unittest.main()