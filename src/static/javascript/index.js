$(document).ready(function(){
    
    //for AJAX requests
    //TODO: Strip # if is here
    var baseUrl = window.location.href;   
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
        $.getJSON(url, function(string) {
            url = baseUrl + string;
            element = "<a href="+url+">Your RDF file!</a>";
            $("#SparqlifiedDownloadLink").html(element);        
        });
    }
    
    
    var $idown;  // Keep it outside of the function, so it's initialized once.
    function downloadURL(url) {
        if ($idown) {
            $idown.attr('src',url);
        } else {
            $idown = $('<iframe>', { id:'idown', src:url }).hide().appendTo('body');
        }
    }
    
});