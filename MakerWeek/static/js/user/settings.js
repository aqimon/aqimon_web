var generalButton=$("#general-submit"), passwordButton=$("#password-submit"), phone;

function enableGeneralButton(){
    generalButton.prop("disabled", false);
}

$("#verify-resend").on("click", function(){
    $("#error-alert-modal").hide();
    $("#verify-resend").html("Loading");
    $("#verify-resend").prop("disabled", true);
    $.getJSON("/ajax/resendPhoneVerification", {"phone": phone}, function(data){
        if (data.result != "success"){
            $("#verify-code-modal").modal('show');
        }
        $("#verify-resend").html("Resend code");
        $("#verify-resend").prop("disabled", false);
    })
})


$("#phone-submit").on("click", function(){
    $("#success-alert").hide();
    $("#error-alert").hide();
    phone = $("#phone").val();
    $("#phone-submit").html("Loading");
    $("#phone-submit").prop("disabled", true);
    $.getJSON("/ajax/initiatePhoneVerification", {"phone": phone}, function(data){
        if (data.result == "invalid number"){
            $("#error").text("Invalid phone number");
            $("#error-alert").show(400);
        } else {
            $("#verify-code-modal").modal('show');
        }
        $("#phone-submit").html("Verify and save");
        $("#phone-submit").prop("disabled", false);
    })
})

$("#verify-submit").on("click", function(){
    $("#error-alert-modal").hide();
    $("#verify-submit").html("Loading");
    $("#verify-submit").prop("disabled", true);
    verifyCode = $("#verify-code").val();
    $.getJSON("/ajax/answerPhoneVerification", {"phone": phone, "verifyCode": verifyCode}, function(data){
        if (data.result == 'success') {
            $("#verify-code-modal").modal('hide');
            $("#success-alert").show(400);
        } else {
            $("#error-modal").text(data.result);
            $("#error-alert-modal").show(400);
        }
        $("#verify-submit").html("Verify code");
        $("#verify-submit").prop("disabled", false);
    })
})

$("#realname, #email").on("input", enableGeneralButton)

$("input[id|=password]").on("input", function(e){
    passwordButton.prop("disabled", false);
})

$("#phone").on("input", function(e){
    $("#phone-submit").prop("disabled", false);
})

generalButton.click(function(){
    $("#success-alert").hide();
    $("#error-alert").hide();
    generalButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Saving');
    generalButton.prop('disabled', true);
    data={
        email: $("#email").val(),
        realname: $("#realname").val(),
        avatar: $('#image-cropper').cropit('export', {
                    type: 'image/jpeg',
                    quality: 0.9
                })
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

$('#image-cropper').cropit({
    $zoomSlider: $(".cropit-image-zoom-input"),
    $fileInput: $(".cropit-image-input"),
    onFileChange: enableGeneralButton,
    onZoomChange: enableGeneralButton,
    onOffsetChange: enableGeneralButton,
    imageState: {
        src: "http://localhost:5000/static/avatar/"+avatar
    }
});
$("#cropit-image-upload-btn").on("click", function(){
    $(".cropit-image-input").click();
})
$("#cropit-rotate-left").on("click", function(){
    $('#image-cropper').cropit("rotateCCW")
})
$("#cropit-rotate-right").on("click", function(){
    $('#image-cropper').cropit("rotateCW")
})