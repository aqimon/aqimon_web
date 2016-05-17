var map, lat=0.0, lon=0.0, events;


function initMap(lat, lon){
    map=new google.maps.Map(document.getElementById("map"), {
        center: {lat: lat, lng: lon},
        mapTypeId: google.maps.MapTypeId.HYBRID,
        zoom: 18
    });
    marker=new google.maps.Marker({
        position: {lat: lat, lng: lon}
    });
    marker.setMap(map)
}

function getData(){
    $.getJSON(sprintf("/api/get/machine/%d", machineID), function(data){
        temperature=[];
        humidity=[];
        dust=[];
        co=[];
        events=data.events;
        for (i=0; i<events.length; i++){
            temperature.push([Date(events[i].time), events[i].temperature]);
            humidity.push([Date(events[i].time), events[i].humidity]);
            dust.push([Date(events[i].time), events[i].dust]);
            co.push([Date(events[i].time), events[i].co]);
        }
        $('#temperature').highcharts().series[0].setData(temperature);
        $('#humidity').highcharts().series[0].setData(humidity);
        $('#dust').highcharts().series[0].setData(dust);
        $('#co').highcharts().series[0].setData(co);
    })
}

$.getJSON(sprintf("/api/get/machine/%d", machineID), function(data){
    initMap(data.latitude, data.longitude)
})

generalSettings={
    xAsix: {
        type: "datetime",
        tickInterval: 7 * 24 * 3600 * 1000, // one week
        tickWidth: 0,
    },
    series: [{
        data: [[Date(0), 0]],
    }]
};

$('#temperature').highcharts(generalSettings);
$('#humidity').highcharts(generalSettings);
$('#dust').highcharts(generalSettings);
$('#co').highcharts(generalSettings);


getData();
setInterval(getData, 1000);