jQuery(function ($) {

    function showMap(pos) {
        var map = new google.maps.Map(document.getElementById('map'), {
            zoom: 18,
            center: new google.maps.LatLng(pos.coords.latitude, pos.coords.longitude),
            mapTypeId: google.maps.MapTypeId.ROADMAP
        });

        var infoWindow = new google.maps.InfoWindow();

        $("#checkins li").each(function () {
            var $this = $(this),
                name = $(this).find('.name').text(),
                dt = $(this).find('.dt').text(),
                lat = parseFloat($(this).find('.lat').text()),
                lng = parseFloat($(this).find('.lng').text());

            var marker = new google.maps.Marker({
                position: new google.maps.LatLng(lat, lng),
                map: map
            });

            google.maps.event.addListener(marker, 'click', function (marker) {
                infoWindow.setContent(name + " at " + dt);
                infoWindow.open(map, marker);
            });
        });
    }

    navigator.geolocation.getCurrentPosition(showMap);

});
