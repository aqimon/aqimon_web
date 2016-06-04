$(function(){
    alerts=[
        "resetSuccess",
        "invalidToken",
        "created",
        "failure"
    ];
    param=location.search;
    for (i=0; i<alerts.length; i++){
        if (("?"+alerts[i])==param){
            $("#"+alerts[i]).show();
        }
    }
});