/**
 * Variables in global scope here:
 *  var CKANEntryId = "{{entityName}}";
 *  var CKANResourceId = "{{resourceId}}";
 */

$(document).ready(function(){
    
    getSparqlifiedResourceNLines(CKANEntryId, CKANResourceId, 50);
    
    function getSparqlifiedResourceNLines(entityName, resourceId, n) {
        var action = "getSparqlifiedResourceNLines/";
        var url = baseUrl + action + CKANEntryId + '/' + CKANResourceId + '/' + n;
        $.getJSON(url, function(stringArray) {
            rdfstring = stringArray.join('');
            
            var myCodeMirror = CodeMirror(function(elt) {
                myTextArea.parentNode.replaceChild(elt, myTextArea);
            }, {value: rdfstring});
        });
    }
    
    $("#Transform_SubmitButton").click(function() {
        // Change link for new RDF file
        // Config link stay the same
        // put the new 50 lines of RDF in the CodeMirror editor
        alert("Does not work yet!");
    });
});