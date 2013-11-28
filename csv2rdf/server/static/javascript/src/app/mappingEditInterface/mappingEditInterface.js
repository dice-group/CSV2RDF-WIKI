angular.module('MappingEditInterface', [])
  .controller('InitCtrl', function ($scope, $log) {
    $log.info(ckan_resource_id); 
    $log.info(wiki_mapping_id); 
  });
