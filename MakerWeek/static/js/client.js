var map, marker, socketio, currentPane, chart, init=false;
var subscribeButton=$("#subscribe-button"), subscribeState="subscribe";

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

function setInfo(data){
    info = data;
    $("#name").text(info.name)
    $("#clientid").text(info.id);
    $("#latitude").text(info.latitude);
    $("#longitude").text(info.longitude);
    $("#address").text(info.address);
    $("#tags").html("");
    for (i=0; i<info.tags.length; i++){
        a=$("<a></a>").prop("href", "/tags/"+encodeURI(info.tags[i])).addClass("label label-info").text(info.tags[i]);
        $("#tags").append(a).append("\n");
    }
}

function initChart(){
    chart=$("#chart")
    chart.highcharts("StockChart", {
            chart: {
                zoomType: "x",

            },
            title: {
                text: "Graph for client "+info.name
            },
            navigator: {
                adaptToUpdatedData: false,
                enabled: false
            },
            scrollbar: {
                liveRedraw: false
            },
            xAxis: {
                type: "datetime",
                minRange: 60*60*3*1000,
                events: {
                    afterSetExtremes: function(e){
                        if ((!e.min) || (!e.max)) return;
                        loadChartData(e.min/1000, e.max/1000);
                    }
                }
            },
            yAxis: [{
                title: {
                    text: "Temperature (°C)",
                },
                opposite: false
            }, {
                title: {
                    text: "Humidity (%)",
                },
                opposite: false
            }, {
                title: {
                    text: "Dust concentration (ppm)"
                }
            }, {
                title: {
                    text: "CO concentration (ppm)"
                }
            }],
            rangeSelector: {
                buttons: [{
                    type: 'hour',
                    count: 3,
                    text: '3h'
                },{
                    type: 'hour',
                    count: 6,
                    text: '6h'
                },{
                    type: 'hour',
                    count: 12,
                    text: '12h'
                },{
                    type: 'day',
                    count: 1,
                    text: '1d'
                },{
                    type: 'week',
                    count: 1,
                    text: '1w'
                },{
                    type: 'month',
                    count: 1,
                    text: '1m'
                },{
                    type: 'month',
                    count: 6,
                    text: '6m'
                },{
                    type: 'ytd',
                    count: 1,
                    text: 'YTD'
                },{
                    type: 'year',
                    count: 1,
                    text: '1y'
                }],
               selected: 8
            },
            series: [{
                type: "line",
                name: "Temperature",
                tooltip: {
                    valueSuffix: "°C"
                },
                data: [],
                yAxis: 0,
            },{
                type: "line",
                name: "Humidity",
                tooltip: {
                    valueSuffix: "%"
                },
                data: [],
                yAxis: 1
            },{
                type: "line",
                name: "Dust concentration",
                tooltip: {
                    valueSuffix: "ppm"
                },
                data: [],
                yAxis: 2
            },{
                type: "line",
                name: "CO concentration",
                tooltip: {
                    valueSuffix: "ppm"
                },
                data: [],
                yAxis: 3
            }]
        });
}

function loadChartData(from, to, callback){
    chart.highcharts().showLoading();
    if (!(to)) to=Math.round(Date.now()/1000);
    console.log("Loading data from", from, "to", to);
    socketio.emit("json", {
        action: "getEventRange",
        clientID: info.id,
        from: from,
        to: to
    }, function(data){
        temperatureArr=[];
        humidityArr=[];
        dustArr=[];
        coArr=[];

        for (var i=0; i<data.length; i++){
            time=data[i].timestamp;
            temperatureArr.push([time, data[i].temperature]);
            humidityArr.push([time, data[i].humidity]);
            dustArr.push([time, data[i].dustLevel]);
            coArr.push([time, data[i].coLevel]);
        }

        chart.highcharts().series[0].setData(temperatureArr);
        chart.highcharts().series[1].setData(humidityArr);
        chart.highcharts().series[2].setData(dustArr);
        chart.highcharts().series[3].setData(coArr);
        chart.highcharts().hideLoading();

        if (callback) callback();
    })
}

function addData(data){
    var time=data.timestamp;
    chart.highcharts().series[0].addPoint([time, data.temperature], redraw=false);
    chart.highcharts().series[1].addPoint([time, data.humidity], redraw=false);
    chart.highcharts().series[2].addPoint([time, data.dustLevel], redraw=false);
    chart.highcharts().series[3].addPoint([time, data.coLevel], redraw=false);
    chart.highcharts().redraw();
}

function timeSubtract(){
    d1=new Date();
    d1.setTime(Date.now());
    d1.setUTCDate(d1.getUTCDate()-1);
    return Math.round(d1.getTime()/1000);
}

$(function(){
    socketio=io("/");

    socketio.on("connect", function(){
        console.log("connected to server");
        if (!init){
            initChart()
            loadChartData(0, null, function(){
                room="client_"+info.id.toString();
                socketio.emit("json", {"action": "joinRoom", "room": room});
            })
            init=true;
        }
    })

    socketio.on("json", function(data){
        console.log("received data");
        addData(data);
    })

    initMap(info.latitude, info.longitude);
    setInfo(info);

    subscribeButton.click(function(){
        subscribeButton.prop("disabled", true);
        subscribeButton.html('<span class="glyphicon glyphicon-refresh spinning"></span> Loading');
        if (subscribeState=="subscribe"){
            $.getJSON("/ajax/notification/subscribe", data={"clientID": info.id}, function(data){
                subscribeButton.prop("disabled", false);
                subscribeButton.html("Unsubscribe");
                subscribeState="unsubscribe";
            })
        } else {
            $.getJSON("/ajax/notification/unsubscribe", {"clientID": info.id}, function(data){
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
            tags: JSON.stringify($("#edit-tags").tagsinput("items"))
        };
        if ($("#edit-private").prop("checked"))
            data.private="true";
        else
            data.private="false";
        $.getJSON("/ajax/edit/client", data, function(res){
            if (res.result == "success"){
                $("#edit-modal-submit-button").html('Save changes');
                $("#edit-modal-submit-button").prop("disabled", false);
                data.tags=JSON.parse(data.tags)
                setInfo(data);
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
        $("#edit-private").prop("checked", info.private);
        $("#edit-tags").tagsinput("removeAll");
        for (i=0; i<info.tags.length; i++)
            $("#edit-tags").tagsinput("add", info.tags[i]);
    })

    $("#edit-tags").tagsinput({
        focusClass: "bootstrap-tagsinput-focus"
    })
}