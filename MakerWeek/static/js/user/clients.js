$(function(){
    $("#edit-location-picker").locationpicker({
        inputBinding: {
            latitudeInput: $("#edit-latitude"),
            longitudeInput: $("#edit-longitude"),
            locationNameInput: $("#edit-address"),
        },
        radius: 0,
        enableAutocomplete: true,
        enableReverseGeocode: true
    });

    $("#add-location-picker").locationpicker({
        location: {
            latitude: 0,
            longitude: 0,
        },
        inputBinding: {
            latitudeInput: $("#add-latitude"),
            longitudeInput: $("#add-longitude"),
            locationNameInput: $("#add-address"),
        },
        radius: 0,
        enableAutocomplete: true,
        enableReverseGeocode: true
    })
})

$("#edit-modal-submit-button").on("click", function(){
    $("#edit-modal-submit-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
    $("#edit-modal-submit-button").prop("disabled", true);
    data = {
        clientID: $("#edit-modal-client-id").text(),
        name: $("#edit-client-name").val(),
        latitude: $("#edit-latitude").val(),
        longitude: $("#edit-longitude").val(),
        address: $("#edit-address").val(),
    };
    $.getJSON("/ajax/edit/client", data, function(data){
        if (data.result == "success"){
            $("#edit-modal-submit-button").html('Save changes');
            $("#edit-modal-submit-button").prop("disabled", false);
        }
    })
})

$("#edit-modal").on("shown.bs.modal", function(e){
    $("#edit-location-picker").locationpicker('autosize');
})

$("#edit-modal").on("show.bs.modal", function(e){
    var button = $(e.relatedTarget);
    var clientID = button.data("clientid");
    $.getJSON("/ajax/get/client", {"clientID": clientID}, function(data){
        $("#edit-modal-client-id").text(data.clientID);
        $("#edit-client-name").val(data.name);
        $("#edit-latitude").val(data.latitude);
        $("#edit-longitude").val(data.longitude);
        $("#edit-address").val(data.address);
    });
})

$("#add-modal").on("shown.bs.modal", function(e){
    $("#add-location-picker").locationpicker('autosize');
})

$("#add-modal-submit-button").on("click", function(){
    $("#add-modal-submit-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
    $("#add-modal-submit-button").prop("disabled", true);
    data = {
        name: $("#add-client-name").val(),
        latitude: $("#add-latitude").val(),
        longitude: $("#add-longitude").val(),
        address: $("#add-address").val(),
    };
    $.getJSON("/ajax/add/client", data, function(data){
        if (data.result == "success"){
            $("#add-modal-submit-button").html('Add client');
            $("#add-modal-submit-button").prop("disabled", false);
            $("#add-modal-clientid").text(data.clientID);
            $("#add-modal-api-key").text(data.apiKey);
            $("#add-modal").modal('hide');
            $("#add-modal-success").modal('show');
        }
    })
})

$("#add-modal").on("show.bs.modal", function(){
    $("#add-client-name").val("");
    $("#add-latitude").val("");
    $("#add-longitude").val("");
    $("#add-address").val("");
})

$("#delete-modal").on("show.bs.modal", function(e){
    var clientID=$(e.relatedTarget).data("clientid");
    $("#delete-modal-clientid").text(clientID);
})

$("#delete-modal-delete-button").on("click", function(){
    $("#delete-modal-delete-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
    $("#delete-modal-delete-button").prop("disabled", true);
    var clientID = $("#delete-modal-clientid").text(clientID);
    $.getJSON("/ajax/delete/client", {clientID: clientID}, function(data){
        if (data.result == "success"){
            $("#delete-alert-success").show(400);
        }
    })
})