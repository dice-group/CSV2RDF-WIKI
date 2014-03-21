angular.module('MappingEditInterface', [])

  .factory('suggestionService', function($http) {
    return {
      getSuggestion: function(mappingName) {
        return $http.get(localhostUri+
                         'suggestMapping?mapping_name='+
                         mappingName)
        .then(function(result) {
          return result.data;
        });
      },
    }

  })

  .factory('mappingsService', function($http) {
    return {
      getMappings: function(ckanResourceId) {
        return $http.get(localhostUri+
                         'getMappings?resource_id='+
                         ckanResourceId)
        .then(function(result) {
          return result.data;
        });
      },
    }
  })

  .controller('EditInterfaceCtrl', function($scope, $log, 
                                            suggestionService,
                                            mappingsService) {
    $scope.mappings = [];
    $log.info(ckanResourceId); 
    $log.info(wikiMappingId); 
    $log.info(localhostUri); 
    $scope.selectedMapping = '';
    $scope.suggestions = [];

    //On load
    mappingsService.getMappings(ckanResourceId).then(function (data) {
      $scope.mappings = data;
      $log.info(data);
    });

    var suggestMapping = function(mapping_name) {
        //Add spinner
        $scope.suggestions = [{uriPrefixed:"Loading..."}];
        $scope.selectedMapping = mapping_name;
        suggestionService.getSuggestion(mapping_name).then(function(data) {
          $scope.suggestions = data;
          if($scope.suggestions.length === 0) {
            $scope.suggestions = [{uriPrefixed:"No suggestions are available!"}];
          }
        });
    };

    $scope.mappingRouter = function(key, value) {
      $log.info(key);
      $log.info(value);
      if(key.match(/col.*/)) {
        suggestMapping(value);
      }
    };

    $scope.wikiTemplate = function() {
      results = [];
      for(var mapping in $scope.mappings) {
        results.push($scope.mappings[mapping].column + 
                  " = " + 
                  $scope.mappings[mapping].name + 
                  " |");
      }
      return results;
    };

    $scope.takeOverSuggestion = function(suggestion) {
      for(var mapping in $scope.mappings) {
        if($scope.mappings[mapping].name == $scope.selectedMapping.name &&
          suggestion.uriPrefixed != "No suggestions are available!" &&
          suggestion.uriPrefixed != "Loading...") {
          $scope.mappings[mapping].name = suggestion.uriPrefixed;
        }
      }
    };



  });
