var generalButton=$("#general-submit"), passwordButton=$("#password-submit");


$("#username, #email").on("input", function(){
    generalButton.prop("disabled", false);
})

$("input[id|=password]").on("input", function(e){
    passwordButton.prop("disabled", false);
})

generalButton.click(function(){
    generalButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Saving');
    generalButton.prop('disabled', true);
    data={
        username: $("#username").val(),
        email: $("#email").val(),
    }
    $.getJSON("/ajax/user_settings/save_general", data, function(data){
        generalButton.html("Save");
        generalButton.prop("disabled", false);
        if (data.result=="success"){
            $("#success-alert").show(400);
        } else {
            $("#error-alert").show(400);
        }
    })
})

passwordButton.click(function(){
    if (($("#password-new").val())!=($("#password-new-repeat").val())) {
        return;
    }
    passwordButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Saving');
    passwordButton.prop('disabled', true);
    data = {
        old_password: $("#password-old").val(),
        new_password: $("#password-new").val(),
    }
    $.getJSON("/ajax/user_settings/change_password", data, function(data){
        passwordButton.html("Save");
        passwordButton.prop("disabled", false);
        if (data.result=="success"){
            $("#success-alert").show(400, function(){
                console.log(window);
                window.location="/login";
            });
        } else {
            $("#error-alert").show(400);
        }
    })
})