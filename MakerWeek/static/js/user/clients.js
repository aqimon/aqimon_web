var deleteButtonTimerID=null;

$("#edit-modal-submit-button").on("click", function(){
    $("#edit-modal-submit-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
    $("#edit-modal-submit-button").prop("disabled", true);
    data = {
        clientID: $("#edit-modal-client-id").text(),
        name: $("#edit-client-name").val(),
        latitude: $("#edit-latitude").val(),
        longitude: $("#edit-longitude").val(),
        address: $("#edit-address").val(),
        tags: JSON.stringify($("#edit-tags").tagsinput('items')),
    };
    console.log(data);
    $.getJSON("/ajax/edit/client", data, function(data){
        if (data.result == "success"){
            $("#edit-modal-submit-button").html('Save changes');
            $("#edit-modal-submit-button").prop("disabled", false);
        }
    })
})

$("#edit-modal").on("shown.bs.modal", function(e){
    $("#edit-location-picker").locationpicker({
        location: {
            latitude: $("#edit-latitude").val(),
            longitude: $("#edit-longitude").val(),
        },
        inputBinding: {
            latitudeInput: $("#edit-latitude"),
            longitudeInput: $("#edit-longitude"),
            locationNameInput: $("#edit-address"),
        },
        radius: 0,
        enableAutocomplete: true,
        enableReverseGeocode: true
    });
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
        $("#edit-tags").tagsinput("removeAll");
        for (i=0; i<data.tags.length; i++)
            $("#edit-tags").tagsinput("add", data.tags[i]);
    });
})

$("#add-modal").on("shown.bs.modal", function(e){
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

$("#add-modal-submit-button").on("click", function(){
    $("#add-modal-submit-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
    $("#add-modal-submit-button").prop("disabled", true);
    data = {
        name: $("#add-client-name").val(),
        latitude: $("#add-latitude").val(),
        longitude: $("#add-longitude").val(),
        address: $("#add-address").val(),
        tags: JSON.stringify($("#add-tags").tagsinput("items"))
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
    $(".delete-modal-clientid").text(clientID);
    $("#delete-modal-delete-button").data("countdown", 5).data("clientid", clientID);
    deleteButtonCountdown();
})

$("#delete-modal").on("hide.bs.modal", function(){
    clearTimeout(deleteButtonTimerID);
})

function deleteButtonCountdown(){
    var second=parseInt($("#delete-modal-delete-button").data("countdown"));
    if (second==0){
        $("#delete-modal-delete-button").prop("disabled", false).html('Delete this client');
    } else {
        $("#delete-modal-delete-button").prop("disabled", true).data("countdown", second-1);
        $("#delete-modal-delete-button").html('Delete this client ('+second.toString()+')');
        deleteButtonTimerID=setTimeout(deleteButtonCountdown, 1000);
    }
}

$("#delete-modal-delete-button").on("click", function(){
    $("#delete-modal-delete-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
    $("#delete-modal-delete-button").prop("disabled", true);
    var clientID = $("#delete-modal-delete-button").data("clientid");
    $.getJSON("/ajax/delete/client", {clientID: clientID}, function(data){
        if (data.result == "success"){
            console.log("x");
            $("#delete-modal").modal("hide");
            $("#delete-success-modal").modal("show");
        }
    })
})

$("#edit-tags").tagsinput({
    focusClass: "bootstrap-tagsinput-focus"
})

$("#add-tags").tagsinput({
    focusClass: "bootstrap-tagsinput-focus"
})