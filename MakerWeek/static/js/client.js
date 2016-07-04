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
        zoom: 15
    });
    marker=new google.maps.Marker({
        position: {lat: latitude, lng: longitude}
    });
    marker.setMap(map)
}

function setInfo(id, name, latitude, longitude, address){
    info = {
        id: id,
        name: name,
        latitude: latitude,
        longitude: longitude,
        address: address
    };
    $("#name").text(name)
    $("#clientid").text(id);
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
            data: [0, 0],
        }]
    };
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
        time=new Date(events[i].timestamp);
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
    var time=data.timestamp;
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
    socketio=io("/");

    socketio.on("connect", function(){
        console.log("connected to server");
        room="client_"+info.id.toString();
        socketio.emit("json", {"action": "getRecentClient", "clientID": info.id}, function(data){
            initChartsData(data);
            socketio.emit("json", {"action": "joinRoom", "room": room});
        })
    })

    socketio.on("json", function(data){
        addData(data);
    })

    $("a[id$=-tab]").on("shown.bs.tab", function(e){
        currentPane=$("#"+$(e.target).attr("aria-controls"));
        currentPane.highcharts().reflow();
        currentPane.highcharts().redraw();
    });

    initCharts();
    initMap(info.latitude, info.longitude);
    setInfo(info.id, info.name, info.latitude, info.longitude, info.address);

    subscribeButton.click(function(){
        subscribeButton.prop("disabled", true);
        subscribeButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
        if (subscribeState=="subscribe"){
            $.getJSON("/ajax/notification/subscribe", data={"clientID": id}, function(data){
                subscribeButton.prop("disabled", false);
                subscribeButton.html("Unsubscribe");
                subscribeState="unsubscribe";
            })
        } else {
            $.getJSON("/ajax/notification/unsubscribe", {"clientID": id}, function(data){
                subscribeButton.prop("disabled", false);
                subscribeButton.html("Subscribe");
                subscribeState="subscribe";
            })
        }
    });
})

if (enableEdit){
    $("#edit-location-picker").locationpicker({
        location: {
            latitude: info.latitude,
            longitude: info.longitude,
        },
        locationName: info.address,
        inputBinding: {
            latitudeInput: $("#edit-latitude"),
            longitudeInput: $("#edit-longitude"),
            locationNameInput: $("#edit-address"),
        },
        radius: 0,
        enableAutocomplete: true,
        enableReverseGeocode: true
    })

    $("#edit-modal-submit-button").on("click", function(){
        $("#edit-modal-submit-button").html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
        $("#edit-modal-submit-button").prop("disabled", true);
        data = {
            clientID: $("#edit-modal-client-id").text(),
            name: $("#edit-client-name").val(),
            latitude: $("#edit-latitude").val(),
            longitude: $("#edit-longitude").val(),
            address: $("#edit-address").val(),
        };
        $.getJSON("/ajax/edit/client", data, function(res){
            if (res.result == "success"){
                $("#edit-modal-submit-button").html('Save changes');
                $("#edit-modal-submit-button").prop("disabled", false);
                setInfo(data.id, data.name, data.latitude, data.longitude, data.address);
                latlng = {
                    lat: parseFloat(data.latitude),
                    lng: parseFloat(data.longitude)
                };
                marker.setPosition(latlng);
                map.panTo(latlng);
            }
        })
    })

    $("#edit-modal").on("shown.bs.modal", function(e){
        $("#edit-location-picker").locationpicker('autosize');
    })

    $("#edit-modal").on("show.bs.modal", function(e){
        $("#edit-modal-client-id").text(info.id);
        $("#edit-client-name").val(info.name);
        $("#edit-latitude").val(info.latitude);
        $("#edit-longitude").val(info.longitude);
        $("#edit-address").val(info.address);
    })
}