var map;
function initMap(){
    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat: -33.8688, lng: 151.2195},
        zoom: 3,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
}

// {machineID:{marker: <markers>, infobox: <infobox>]}
markersList={};
currentOpenInfobox=null;

function setClient(data){
    var clientID=data.clientID;
    data.time=Date(data.time).toString()
    if (clientID in markersList) {
        markersList[clientID].infobox.setContent(generateContent(data));
        markersList[clientID].marker.setAnimation(google.maps.Animation.BOUNCE);
        setTimeout(function(client){
            console.log(client);
            client.marker.setAnimation(null);
        }, 1000, markersList[clientID]);
    } else {
        markersList[clientID]=newMarker(data);
        markersList[clientID].marker.setAnimation(google.maps.Animation.DROP);
    }
}
function newMarker(data){
    var marker=new google.maps.Marker({
        position: {lat: data.latitude, lng: data.longitude},
        map: map,
        title: sprintf("Client %(clientID)s", data)
    });
    var infobox=new google.maps.InfoWindow({
        content: generateContent(data)
    });
    marker.addListener("click", function(){
        if (currentOpenInfobox!=null){
            currentOpenInfobox.close()
        }
        infobox.open(map, marker);
        currentOpenInfobox=infobox;
    });
    return {marker: marker, infobox: infobox};
}

function generateContent(data){
    var contentString=
        '<div class="infobox"> \
            <div class="infobox-header"> \
                Client ID: %(clientID)s<br /> \
            </div> \
            <hr class="infobox-hr"/> \
            <div class="infobox-content"> \
                <b>Latitude</b>: %(latitude).3f<br /> \
                <b>Longitude</b>: %(longitude).3f<br /> \
                <b>Address</b>: %(latitude)s<br /> \
                <b>Temperature</b>: %(temperature).3f<br /> \
                <b>Humidity</b>: %(humidity).3f<br /> \
                <b>Dust concentration</b>: %(dustLevel).3f<br /> \
                <b>CO concentration</b>: %(coLevel).3f<br /> \
                <b>Timestamp</b>: %(time)s <br /> \
            </div> \
            <div class="infobox-moreinfo"> \
                <b><a href="/client/%(clientID)s">More info</a></b> \
            <div> \
        </div>';
    var contentString=sprintf(contentString, data);
    return contentString;
}

$(function(){
    // First we initialize Socket.IO
    socketio=io("/");

    socketio.on("connect", function (){
        console.log("connected to server");
        socketio.emit("json", {"action": "getRecent"}, function (data){
            for (i=0; i<data.length; i++){
                setClient(data[i]);
            }
        });
        socketio.emit("json", {"action": "joinRoom", "room": "index"})
    });

    socketio.on("connect_error", function (data){
        console.log("error: ", data);
    });

    socketio.on("json", function (data){
        setClient(data);
    });

    // Now comes the map
    initMap();
})

