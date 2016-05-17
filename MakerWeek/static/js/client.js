var map, marker, socketio, currentPane;

function initMap(latitude, longitude){
    map=new google.maps.Map(document.getElementById("map"), {
        center: {lat: latitude, lng: longitude},
        mapTypeId: google.maps.MapTypeId.HYBRID,
        zoom: 1
    });
    marker=new google.maps.Marker({
        position: {lat: latitude, lng: longitude}
    });
    marker.setMap(map)
}

function initInfo(latitude, longitude, address){
    $("#latitude").text(latitude);
    $("#longitude").text(longitude);
    $("#address").text(address);
}

function generateSettings(data){
    var generalSettings={
        chart: {
            type: "line"
        },
        xAxis: {
            type: "datetime",
            tickInterval: 10 * 60 * 1000 // 10 minutes
        },
        series: [{
            data: [],
        }]
    };
    generalSettings.series[0].data=data;
    return generalSettings
}


function initCharts(events){
    temperatureArr=[];
    humidityArr=[];
    dustLevelArr=[];
    coLevelArr=[];

    for (var i=0; i<events.length; i++) {
        time=events[i].time;
        temperatureArr.push([time, events[i].temperature]);
        humidityArr.push([time, events[i].humidity]);
        dustLevelArr.push([time, events[i].dustLevel]);
        coLevelArr.push([time, events[i].coLevel]);
    }

    $("#temperature").highcharts(generateSettings(temperatureArr));
    $("#humidity").highcharts(generateSettings(humidityArr));
    $("#dustLevel").highcharts(generateSettings(dustLevelArr));
    $("#coLevel").highcharts(generateSettings(coLevelArr));

    $("#temperature").highcharts().redraw();
    currentPane=$("#temperature");
}

function addData(data){
    var time=data.time;
    console.log(data.humidity);
    $("#temperature").highcharts().series[0].addPoint([time, data.temperature], redraw=false, shift=true);
    $("#humidity").highcharts().series[0].addPoint([time, data.humidity], redraw=false, shift=true);
    $("#dustLevel").highcharts().series[0].addPoint([time, data.dustLevel], redraw=false, shift=true);
    $("#coLevel").highcharts().series[0].addPoint([time, data.coLevel], redraw=false, shift=true);
    if (typeof(currentPane) != "undefined") {
        currentPane.highcharts().redraw();
    }
}

function reflowAndRedraw(e){
    currentPane=$("#"+$(e.target).attr("aria-controls"));
    currentPane.highcharts().reflow();
    currentPane.highcharts().redraw();
}

$(function(){
    socketio=io("/");

    socketio.on("connect", function(){
        console.log("connected to server");
        room=sprintf("client_%s", clientID);
        socketio.emit("json", {"action": "joinRoom", "room": room});
    })

    socketio.on("json", function(data){
        addData(data);
    })

    $("a[id$=-tab]").on("shown.bs.tab", function(e){
        currentPane=$("#"+$(e.target).attr("aria-controls"));
        currentPane.highcharts().reflow();
        currentPane.highcharts().redraw();
    });

    $.getJSON(sprintf("/api/get/client/%s", clientID), function(data){
        initMap(data.latitude, data.longitude);
        initInfo(data.latitude, data.longitude, data.address);
        initCharts(data.recentEvents);
    })
})