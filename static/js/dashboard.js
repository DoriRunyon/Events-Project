


function showEvents(result) {
 
    $(".related-artists-imgs").remove();
    $(".event").remove();

    

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
            eventContainer.append("<a href="+songkick_link+">Buy Tickets</a>");
            eventContainer.append(saveButton);
            eventContainer.append("<hr/>");

            $("#event-results").append(eventContainer);


        
     }


     for (i=0; i< result.related_artist_names_imgs.length; i++) {

        $('.related-artists').append("<span class='related-artists-imgs'><img id="+result.related_artist_names_imgs[i][0]+" src="+result.related_artist_names_imgs[i][1]+"></span>");

      }

      $('.related-artists-imgs').click(function(evt) {
 
                var artist_name = evt.target.id.replace(/[_-]/g, " ");
                $("#artist").val(artist_name);
                $("#city").val();
                alert("Hey this is gonna take a while.. sorry :(");
                getFormInputs();
        });
    
    }




function getFormInputs(evt) {

    if (evt) {
        evt.preventDefault();
    }

    findEvents($("#artist").val(), $("#city").val());

}

function findEvents(artist, city) {


    var userInputs = {'artist': artist, 'city': city};

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
        alert("You saved: "+eventName);

}



function initMap() {

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
    $("#playlists").append("<h3>"+playlistName+"</h3>");

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



google.maps.event.addDomListener(window, 'load', initMap);

$('#search-shows').click(getFormInputs);
$('#create-playlist').click(createPlaylist);



