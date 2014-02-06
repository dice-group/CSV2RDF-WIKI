$(document).ready(function(){
    
    //for AJAX requests
    var CKANEntryId = '';
    var CKANResourceId = '';
    
    function getCKANEntity(CKANEntryId) {
        var action = "getCKANEntity/";
        var url = baseUrl + action + CKANEntryId;
        $.getJSON(url, function(model) {
            //render the received object
            //templates
            console.log(model);
            $.get("static/templates/entity.mustache", function(view) {
                var entity = $.mustache(view, model);
                
                console.log(entity);
                $("#CKANEntityContainer").html(entity);
                
                CKANResourceId_SubmitButton_register();
            });
        });
    }
    
    //Events
    
    $("#CKANEntryId_SubmitButton").click(function() {
        CKANEntryId = $("#CKANEntryId_Input").val();
        getCKANEntity(CKANEntryId);
    });
    
    function CKANResourceId_SubmitButton_register() {
        $("#CKANResourceId_SubmitButton").click(function(){
            $.each($(".CKANResourceId_RadioButton"), function() {
                if($(this).attr('checked') === 'checked') {
                    CKANResourceId = $(this).val();
                    processResource(CKANEntryId, CKANResourceId)
                }                
            });
        }); 
    }
    
    function processResource(CKANEntryId, CKANResourceId) {
        var action = "processResource/";
        var url = baseUrl + action + CKANEntryId + '/' + CKANResourceId;
        var configUrl = wikiBaseUrl + wikiNamespace + CKANResourceId;
        var element = '';
        $.getJSON(url, function(string) {
            if(string === null) {
                element = "<a href="+configUrl+">Please create a config for this resource.</a>"
                $("#SparqlifiedDownloadLink").html(element);        
            } else {
                $("#entityName").val(CKANEntryId);
                $("#resourceId").val(CKANResourceId);
                $("#proceedToRDF").show();
                url = baseUrl + string;
            }
                    
        });
    }
    
});