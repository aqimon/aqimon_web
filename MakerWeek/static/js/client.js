var map;

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

function initInfo(latitude, longitude, address){
    $("#latitude").text(latitude);
    $("#longitude").text(longitude);
    $("#address").text(address);
}

function initCharts(events){
    var generalSettings={
        chart: {
            type: "line"
        },
        xAxis: {
            type: "datetime",
            tickInterval: 60 * 60 * 1000 // one hour
        },
        series: [{
            data: []
        }]
    };
    $('#temperature').highcharts(generalSettings);
    $('#humidity').highcharts(generalSettings);
    $('#dustLevel').highcharts(generalSettings);
    $('#coLevel').highcharts(generalSettings);

    for (i=0; i<events.length; i++) {
        console.log(events[i]);
        var time=events[i].time;
        $("#temperature").highcharts().series[0].addPoint([time, events[i].temperature], redraw=false);
        $("#humidity").highcharts().series[0].addPoint([time, events[i].humidity], redraw=false);
        $("#dustLevel").highcharts().series[0].addPoint([time, events[i].dustLevel], redraw=false);
        $("#coLevel").highcharts().series[0].addPoint([time, events[i].coLevel], redraw=false);
    }
    $("#temperature").highcharts().reflow();
    $("#temperature").highcharts().redraw();
    $("#humidity").highcharts().redraw();
    $("#dustLevel").highcharts().redraw();
    $("#coLevel").highcharts().redraw();
}

function addData(data){
    var time=Date(data.time);
    $("#temperature").highcharts().series[0].addPoint([time, data.temperature]);
    $("#humidity").highcharts().series[0].addPoint([time, data.humidity]);
    $("#dustLevel").highcharts().series[0].addPoint([time, data.dustLevel]);
    $("#coLevel").highcharts().series[0].addPoint([time, data.coLevel]);
}

function reflowAndRedraw(e){
    targetPane=$("#"+$(e.target).attr("aria-controls"));
    targetPane.highcharts().reflow();
    targetPane.highcharts().redraw();
}

$(function(){
    socketio=io("/");
    socketio.on("connect", function(){
        console.log("connected to server");
        room=sprintf("client_%s", clientID);
        socketio.emit("json", {"action": "joinRoom", "room": room});
    });
    socketio.on("json", function(data){
        addData(data);
    })
    $.getJSON(sprintf("/api/get/client/%s", clientID), function(data){
        console.log("received: ", data)
        //initMap(data.latitude, data.longitude);
        initInfo(data.latitude, data.longitude, data.address);
        initCharts(data.recentEvents);
        $("#temperature-tab").on("shown.bs.tab", reflowAndRedraw);
        $("#humidity-tab").on("shown.bs.tab", reflowAndRedraw);
        $("#dustLevel-tab").on("shown.bs.tab", reflowAndRedraw);
        $("#coLevel-tab").on("shown.bs.tab", reflowAndRedraw);
    })
})