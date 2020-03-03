;(function(p,l,o,w,i,n,g){if(!p[i]){p.GlobalSnowplowNamespace=p.GlobalSnowplowNamespace||[];
p.GlobalSnowplowNamespace.push(i);p[i]=function(){(p[i].q=p[i].q||[]).push(arguments)
};p[i].q=p[i].q||[];n=l.createElement(o);g=l.getElementsByTagName(o)[0];n.async=1;
n.src=w;g.parentNode.insertBefore(n,g)}}(window,document,"script","https://sp-js.apps.gov.bc.ca/MDWay3UqFnIiGVLIo7aoMi4xMC4y.js","snowplow"));
var collector = 'spm.gov.bc.ca';

window.snowplow('newTracker','rt',collector, {
    appId: "Snowplow_standalone",
    platform: 'web',
    post: true,
    forceSecureTracker: true,
    contexts: {
        webPage: true,
        performanceTiming: true
        }
    });
    window.snowplow('enableActivityTracking', 30, 30); // Ping every 30 seconds after 30 seconds
    window.snowplow('enableLinkClickTracking');
    window.snowplow('trackPageView');
    
    // Google Maps Tracking

    // The Snowplow call that passes marker click data to the collector.
    function mapTracker(data) {
        window.snowplow('trackSelfDescribingEvent', {
            schema: "iglu:ca.bc.gov.googlemaps/stop_overdose_marker_click/jsonschema/1-0-0",
            data: {
                geo_latitude: data.LATITUDE.toString(),
                geo_longitude: data.LONGITUDE.toString(),
                name: data.SV_NAME,
                description: data.SV_DESCRIPTION,
                hours : data.HOURS,
                phone:  data.PHONE_NUMBER,
                email:  data.EMAIL_ADDRESS,
                address:  data.STREET_NUMBER
            }
        });
    }

    // The Snowplow call that passes the map search context data to the collector.
    // This function could be called from the drupal submit handler, on successful
    // submit of the map search form. 
    // The developer will have to retrieve these values and then set these variables
    // in the backend submit handler and pass it to the function.
    function trackContext(keyword_search, select_city) {
        window.snowplow('trackSelfDescribingEvent', {
            schema: "iglu:ca.bc.gov.googlemaps/marker_click/jsonschema/1-0-0",
            data: {
                keywords: keyword_search,
                city: select_city,
            }
        });
    }

    /*  Add click Listener and callback function to the marker. 
        This function will need to called upon creation of new
        Map Markers. 

        Example: 

        |    marker = new google.maps.Marker({
        |        map: map,
        |        position: {lat: 59.327, lng: 18.067}
        |        data: {\\ This object will contain the marker data 
        |               \\ (lat, long, SV_NAME, etc.) to be passed to the schema
        |        }
        |    });
        |    marker.addListener('click', mapTracker(marker.data));
        
         
        Further documentation and examples exist in the Google Maps
        API Documentation here:

        https://developers.google.com/maps/documentation/javascript/markers#animate
    */



    // Youtube Embed Video Tracking

    // Gets called when the youtube player changes state, and sends
    // and triggers a snowplow event with player status info.
    function onPlayerStateChange(event) {
        var player_info = {
            status: '', 
            video_id: event.target.getVideoData().video_id,
            video_src: event.target.getVideoUrl(),
            title: event.target.getVideoData().title,
            author: event.target.getVideoData().author,
            time: event.target.getCurrentTime()
        };

        switch(event.data) {
            case YT.PlayerState.PLAYING:
                player_info.status = 'Playing';
                track_youtube_player(player_info);
                break;
            case YT.PlayerState.PAUSED:
                player_info.status = 'Paused';
                track_youtube_player(player_info);
                break;
            case YT.PlayerState.ENDED:
                player_info.status = 'Ended';
                track_youtube_player(player_info);
                break;
            default:
        return;
        }
    }
    
    // This function gets called when the Youtube Iframe API has finished loading. 
    // The following are two examples of creating the youtube player object, but 
    // Stop Overdose may have a different implementation.
    // If the embed iframes are hardcoded and not generated with the API, you could
    // add a new class to each iframe element and loop through them, adding the events and callbacks.
    // Wherever this is being called to create the YouTube
    // embeds, add the following two event listeners (and their callbacks) to the player object:
    //  'onReady': onPlayerReady, 'onStateChange': onPlayerStateChange.
    /*
    
    |   function onYouTubeIframeAPIReady() {
    |       yt_players = document.getElementsByClassName('youtube_player');
    |       for (var i = 0; i < yt_players.length; i++) {
    |           player = new YT.Player(yt_players.item(i).id, {
    |               events: {
    |                  'onReady': onPlayerReady,
    |                  'onStateChange': onPlayerStateChange
    |               }
    |           });
    |        }
    |    }

    |   function onYouTubeIframeAPIReady() {
    |      player = new YT.Player(// Insert unique ID of embed iFrame. Ex: 'player' //, {
    |          events: {
    |              'onReady': onPlayerReady,
    |               'onStateChange': onPlayerStateChange
    |           }
    |       });
    |   }
    */

    // This will get called by the API once the youtube player is ready
    // and then calls the youtube tracker function.
    function onPlayerReady(event) {
        var player_info = {
            status: 'Ready', 
            video_id: 'Not Available', // Video ID not available on ready state
            video_src: event.target.getVideoUrl(),
            title: event.target.getVideoData().title,
            author: event.target.getVideoData().author,
            time: event.target.getCurrentTime()
        };
        track_youtube_player(player_info);
    }

    // Send snowplow event with youtube player state.
    function track_youtube_player(player_info) {
        window.snowplow('trackSelfDescribingEvent', {
            schema: "iglu:ca.bc.gov.youtube/youtube_playerstate/jsonschema/1-0-0",
            data: {
                status: player_info.status,
                video_src: player_info.video_src,
                video_id: player_info.video_id,
                title: player_info.title,
                author: player_info.author, 
                time: player_info.time
            }
        });
    }
