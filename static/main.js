var map;
function initAutocomplete() {
        map = new google.maps.Map(document.getElementById('map'), {
          center: {lat: -33.8688, lng: 151.2195},
          zoom: 3,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        });

        // Create the search box and link it to the UI element.
        var input = document.getElementById('pac-input');
        var searchBox = new google.maps.places.SearchBox(input);
        map.controls[google.maps.ControlPosition.TOP_LEFT].push(input);

        // Bias the SearchBox results towards current map's viewport.
        map.addListener('bounds_changed', function() {
          searchBox.setBounds(map.getBounds());
        });

        var markers = [];
        // Listen for the event fired when the user selects a prediction and retrieve
        // more details for that place.
        searchBox.addListener('places_changed', function() {
          var places = searchBox.getPlaces();

          if (places.length == 0) {
            return;
          }

          // Clear out the old markers.
          markers.forEach(function(marker) {
            marker.setMap(null);
          });
          markers = [];

          // For each place, get the icon, name and location.
          var bounds = new google.maps.LatLngBounds();
          places.forEach(function(place) {
            var icon = {
              url: place.icon,
              size: new google.maps.Size(71, 71),
              origin: new google.maps.Point(0, 0),
              anchor: new google.maps.Point(17, 34),
              scaledSize: new google.maps.Size(25, 25)
            };

            // Create a marker for each place.
            markers.push(new google.maps.Marker({
              map: map,
              icon: icon,
              title: place.name,
              position: place.geometry.location
            }));

            if (place.geometry.viewport) {
              // Only geocodes have viewport.
              bounds.union(place.geometry.viewport);
            } else {
              bounds.extend(place.geometry.location);
            }
          });
          map.fitBounds(bounds);
        });
      }

// machineID:{markers, infobox}
markersList={};

function process(data){
    // Going through the new data
    for (i=0; i<data.length; i++){
        if (!(data[i].machineID in markersList)) {
            markersList[data[i].machineID.toString()]=createPoint(data[i]);
        } else {
            markersList[data[i].machineID.toString()].infobox.setContent(generateContentString(data[i]))
        }
    }
    // Going through the old one
    idList=[];
    for (i=0; i<data.length; i++){
        idList.push(data[i].machineID)
    }
    for (var k in markersList){
        if ($.inArray(parseInt(k), idList)==-1){
            markersList[k].marker.setMap(null);
            delete markersList[k];
        }
    }
}


function getData(){
    $.getJSON("/api/get/recent", function (data){
        process(data);
    });
}

function generateContentString(data){
    var contentString=
        '<div class="infobox"> \
            <div class="infobox-header"> \
                Machine ID: %(machineID)s<br /> \
            </div> \
            <div class="infobox-content"> \
                Latitude: %(latitude).3f<br /> \
                Longitude: %(longitude).3f<br /> \
                Temperature: %(temperature).3f<br /> \
                Humidity: %(humidity).3f<br /> \
                Dust: %(dustLevel).3f<br /> \
                CO: %(coLevel).3f<br /> \
            </div> \
            <div class="infobox-moreinfo"> \
                <a href="/machine/%(machineID)s">More info</a> \
            <div> \
        </div>';
    contentString=sprintf(contentString, data);
    return contentString;
}

function createPoint(data){
    pos=new google.maps.LatLng(data.latitude, data.longitude);
    marker=new google.maps.Marker({
        position: pos,
        title: sprintf("Machine %d", data.machineID)
    });

    var infoWindow=new google.maps.InfoWindow({
        content: generateContentString(data),
        position: pos
    });

    marker.addListener('click', function(){
        infoWindow.open(map);
    });

    marker.setMap(map);

    return {marker: marker, infobox: infoWindow};
}

setInterval(getData, 5000);