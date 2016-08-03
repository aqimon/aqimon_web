var generalButton=$("#general-submit"), passwordButton=$("#password-submit");


$("#phone, #realname, #email").on("input", function(){
    generalButton.prop("disabled", false);
})

$("input[id|=password]").on("input", function(e){
    passwordButton.prop("disabled", false);
})

generalButton.click(function(){
    $("#success-alert").hide();
    $("#error-alert").hide();
    generalButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Saving');
    generalButton.prop('disabled', true);
    data={
        email: $("#email").val(),
        phone: $("#phone").val(),
        realname: $("#real").val()
    }
    $.post("/ajax/user_settings/save_general", data, function(data){
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
    $("#success-alert").hide();
    $("#error-alert").hide();
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

$('#image-cropper').cropit();
$('#image-cropper').cropit("imageSrc", "https://a.thumbs.redditmedia.com/g1LcJBivSVWumldk-5AV9mDLjLCaPhzTJuq87NOoeW4.jpg");