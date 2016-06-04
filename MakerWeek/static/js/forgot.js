var buttonState=true;
function changeButtonState(){
    var button=$("#submit-button");
    if (buttonState) {
        button.prop("disabled", true);
        button.html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
        buttonState=false;
    } else {
        button.prop("disabled", false);
        button.html('Reset my password');
        buttonState=true;
    }
}

function hideAlerts(){
    $(".alert-success").hide();
    $(".alert-danger").hide();
}


function handleResponse(data){
    data=JSON.parse(data);
    if (data.result=="success"){
        $(".alert-success").show(400);
    } else {
        $(".alert-danger").show(400);
    }
    changeButtonState();
}

$(function(){
    $("#submit-button").on("click", function(){
        changeButtonState();
        hideAlerts();
        email=$("#email").val();
        $.post("/forgot", {"email": email}, handleResponse);
    });
});