$(document).ready( function() {


function showEvents(result) {


 
    $(".related-artists-imgs").remove();
    $(".event").remove();

    if (result.error_message !== null) {
        $("#show-message").text("Oops something went wrong, no artist could be found. Please try again.");
    }

    if (result.events.length < 1) {

        var artist_name = result.searched_artist_name_img[0].replace(/[_-]/g, " ");
        $("#show-message").text("Sorry, no shows found. Select another artist below to run a new search.");
        $("#related-artists-for-artist").text("Artists similar to "+artist_name);
    }

    else {

        var artist_name = result.searched_artist_name_img[0].replace(/[_-]/g, " ");
        $("#show-message").text("Shows for artists similar to "+artist_name);
        $("#related-artists-for-artist").text("Artists similar to "+artist_name);
    }


    for (i=0; i< result.events.length; i++) {

            var event_name = result.events[i][1]['event_name'];
            var event_city = result.events[i][1]['city'];
            var songkick_link = result.events[i][1]['songkick_link'];
            var event_songkick_id = result.events[i][1]['id'];

            var eventContainer = $("<div class='event'></div>");

            var saveButton = $("<button id="+event_songkick_id+"></button>");
            saveButton.text("Save Show");
            $(saveButton).click(saveShow);

            eventContainer.append("<p id='eventname'>"+event_name+"</p>");
            eventContainer.append("<p>"+event_city+"</p>");
            eventContainer.append("<a class='buy-tickets' href="+songkick_link+">Buy Tickets</a>");
            eventContainer.append(saveButton);
            eventContainer.append("<hr/>");

            $("#event-results").append(eventContainer);


        
     }


     for (i=0; i< result.related_artist_names_imgs.length; i++) {


        var artistNameforimg = result.related_artist_names_imgs[i][0].replace(/-/g, " ");
        $('.related-artists').append("<span class='related-artists-imgs'><img id="+result.related_artist_names_imgs[i][0]+" src="+result.related_artist_names_imgs[i][1]+"></span>");

      }

      $('.related-artists-imgs').click(function(evt) {
 
                var artist_name = evt.target.id.replace(/[_-]/g, " ");
                $("#artist").val(artist_name);
                $("#city").val();
                getFormInputs();
        });
    
    }




function getFormInputs(evt) {

    if (evt) {
        evt.preventDefault();
    }

    console.log($('#artist').val());
    console.log($('#city').val());
    findEvents($("#artist").val(), $("#city").val());

}

function findEvents(artist, city) {

    var userInputs = {'artist': artist, 'city': city};

    // if (window.location.href === 'http://localhost:5000/') {

    // window.location.href = "http://localhost:5000/dashboard?artist="+artist+"?city="+city;

    // }

    $.get("/search-for-shows.json",
        userInputs,
        showEvents);
}

function saveShow(evt) {

    var eventSongkickid = {'event_songkick_id': evt.target.id};

    $.get("/save-show.json",
        eventSongkickid,
        showUserSavedEvents);

}

function showUserSavedEvents(result) {


        var eventName = result.event_name;
        alert("You saved: " + eventName);
    


}



function initMap() {

 
    geocoder = new google.maps.Geocoder();


    var myLatLng = {lat: 40.7306, lng: -73.935242};
    var bounds = new google.maps.LatLngBounds();

    var map = new google.maps.Map(document.getElementById('map'), {
        center: myLatLng,
        zoom: 2,
    });

    var oldMarker = new google.maps.Marker({

            position: myLatLng,
            map: map,
            title: 'Center.'
 });

        var infoWindow = new google.maps.InfoWindow({
                content: "holding..."
            });

        for (i=0; i< locations.length; i++) {

            var marker_lat = parseFloat(locations[i][0]);
            var marker_lng = parseFloat(locations[i][1]);
            var eventInfo = locations[i][2];
            eventInfo = '<p>' + eventInfo + '</p>';


            var position = new google.maps.LatLng(marker_lat, marker_lng);
            var marker = new google.maps.Marker({
                position: position,
                map: map,
                title: eventInfo,
                info: eventInfo,
                icon: '/static/images/musicnote2.png'

            });
            google.maps.event.addListener(marker, 'click', function () {
                infoWindow.setContent(this.info);
                infoWindow.open(map, this);
            });
    }

}

function showPlaylist(result) {


    var playlistName = result.playlistName;
    console.log(playlistName);
    $(".panel-group").show();
    $("#playlist-name").append("<a data-toggle='collapse' href='#collapse1'>"+playlistName+"</a>");

    for (i=0; i< result.tracks.length; i++) {

        console.log(result.tracks[i]);
        $("#playlists").append("<li>"+result.tracks[i]+"</li>");
    

    }


}

function createPlaylist() {

    var playlistName = prompt("What would you like to call your playlist?");

    var performingArtistsList= "";

    for (i=0; i< performingArtists.length; i++) {

        performingArtistsList = performingArtistsList + "+" + performingArtists[i];
    }

    var userInputs = {'performingArtistsList': performingArtistsList, 'playlistName': playlistName};

    $.get("/make-playlist.json",
        userInputs,
        showPlaylist);

}

var geocoder;

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(successFunction, errorFunction);
}
//Get the latitude and the longitude;
function successFunction(position) {
    var lat = position.coords.latitude;
    var lng = position.coords.longitude;
    codeLatLng(lat, lng);
}

function errorFunction(){
    alert("Geocoder failed");
}


function codeLatLng(lat, lng) {

    var latlng = new google.maps.LatLng(lat, lng);
    geocoder.geocode({'latLng': latlng}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
      console.log(results);
        if (results[1]) {
         //formatted address
         // alert(results[0].formatted_address);
        //find country name
             for (var i=0; i<results[0].address_components.length; i++) {
            for (var b=0;b<results[0].address_components[i].types.length;b++) {

            //there are different types that might hold a city admin_area_lvl_1 usually does in come cases looking for sublocality type will be more appropriate
                if (results[0].address_components[i].types[b] == "locality") {
                    //this is the object you are looking for
                    city= results[0].address_components[i];
                    break;
                }
            }
        }
        //city data
        // alert(city.long_name);
        var myCity = city.long_name;
        $("#city").val(myCity);


        } else {
          alert("No results found");
        }
      } else {
        alert("Geocoder failed due to: " + status);
      }
    });
  }

google.maps.event.addDomListener(window, 'load', initMap);


$('.btn').on('click', function() {
    var $this = $(this);
  $this.button('loading');
    setTimeout(function() {
       $this.button('reset');
   }, 4000);
});

$('#search-shows').click(getFormInputs);
$('#create-playlist').click(createPlaylist);

});

