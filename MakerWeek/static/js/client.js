var map, marker, socketio, currentPane, pointCount=0, obj={};
var subscribeButton=$("#subscribe-button"), subscribeState="subscribe";
var specificSettings={
    title: {
        temperature: "Temperature (degree Celsius)",
        humidity: "Humidity (%)",
        dustLevel: "Dust concentration (m^3)"
    }
};

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
            type: "line",
            zoomType: "x",
        },
        credits: {
            enabled: false
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

function initCharts(){
    obj.temperature=$("#temperature").highcharts(generateSettings("temperature"));
    obj.humidity=$("#humidity").highcharts(generateSettings("humidity"));
    obj.dustLevel=$("#dustLevel").highcharts(generateSettings("dustLevel"));
    obj.coLevel=$("#coLevel").highcharts(generateSettings("coLevel"));

    obj.temperature.highcharts().showLoading();
    obj.humidity.highcharts().showLoading();
    obj.dustLevel.highcharts().showLoading();
    obj.coLevel.highcharts().showLoading();

    obj.temperature.highcharts().redraw();
    currentPane=$("#temperature");
}

function initChartsData(events){
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
        pointCount++;
    }

    obj.temperature.highcharts().series[0].setData(temperatureArr);
    obj.humidity.highcharts().series[0].setData(humidityArr);
    obj.dustLevel.highcharts().series[0].setData(dustLevelArr);
    obj.coLevel.highcharts().series[0].setData(coLevelArr);

    obj.temperature.highcharts().hideLoading();
    obj.humidity.highcharts().hideLoading();
    obj.dustLevel.highcharts().hideLoading();
    obj.coLevel.highcharts().hideLoading();
}

function addData(data){
    var time=data.time;
    if (pointCount>100){
        shift=true;
    } else {
        shift=false;
        pointCount++;
    }
    $("#temperature").highcharts().series[0].addPoint([time, data.temperature], redraw=false, shift=shift);
    $("#humidity").highcharts().series[0].addPoint([time, data.humidity], redraw=false, shift=shift);
    $("#dustLevel").highcharts().series[0].addPoint([time, data.dustLevel], redraw=false, shift=shift);
    $("#coLevel").highcharts().series[0].addPoint([time, data.coLevel], redraw=false, shift=shift);
    if (typeof(currentPane) != "undefined") {
        currentPane.highcharts().redraw();
    }
}

$(function(){
    var lock=false;
    socketio=io("/");

    socketio.on("connect", function(){
        console.log("connected to server");
        room="client_"+clientID.toString();
        socketio.emit("json", {"action": "joinRoom", "room": room});
    })

    socketio.on("json", function(data){
        while (lock);
        addData(data);
    })

    $("a[id$=-tab]").on("shown.bs.tab", function(e){
        currentPane=$("#"+$(e.target).attr("aria-controls"));
        currentPane.highcharts().reflow();
        currentPane.highcharts().redraw();
    });

    initCharts();

    $.getJSON("/ajax/get/client", {"clientID": clientID}, function(data){
        initMap(data.latitude, data.longitude);
        initInfo(data.latitude, data.longitude, data.address);
        lock=true;
        initChartsData(data.events);
        lock=false;
    })

    subscribeButton.click(function(){
        subscribeButton.prop("disabled", true);
        subscribeButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
        if (subscribeState=="subscribe"){
            $.getJSON("/ajax/notification/subscribe", data={"clientID": clientID}, function(data){
                subscribeButton.prop("disabled", false);
                subscribeButton.html("Unsubscribe");
                subscribeState="unsubscribe";
            })
        } else {
            $.getJSON("/ajax/notification/unsubscribe", {"clientID": clientID}, function(data){
                subscribeButton.prop("disabled", false);
                subscribeButton.html("Subscribe");
                subscribeState="subscribe";
            })
        }
    })

})
