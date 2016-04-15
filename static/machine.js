var map, lat=0.0, lon=0.0, events;

function refresh(){
    $.getJSON(sprintf("/api/get/machine/%d", machineID), function(data){
        lat=data.latitude;
        lon=data.longitude;
        events=data.events;
        update
    })
}

function initMap(){
    map=new google.maps.Map(document.getElementById("map"), {
        center=
    })
}