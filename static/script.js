// Check if we are testing or not:
const DEBUG = (window.location.hostname == '127.0.0.1') ? true : false

$(document).ready(function() {
    // Rather than let DataTables do the ajax, which is annoying, why don't we do it?
    var table = $('#myTable').DataTable({
      "ajax": {
        "url": "/api/all",
        "dataSrc": "data"
      },
      "columns": [
        { "data": "country" },
        { "data": "city" },
        { "data": "ref" },
        { "data": "reader" },
        { "data": "year" },
        { "data": "HULTP" },
      ],
      // Set up the last column as the hyperlink to the listen. TODO: Turn into a button and a GET request
      "columnDefs": [ {
        "targets": 6,
        "data": "HULTP",
        "render": function ( data ) {
            return '<a href="/listen?HULTP='+ data+'">Play</a>';
        }
      },
     ]
    })
    .on( 'search.dt', function () {
        // Get all of the cities being displayed
        let focusCities = distinct(table.column( 1, {search: 'applied'}).data())
        focusMap(focusCities)
    } );
  })
function distinct(array){
    let distinctArray = []
    for(let i = 0; i < array.length; i++) {
        if (!distinctArray.includes(array[i])) {
            // if not, add it to the unique array
            distinctArray.push(array[i]);
        }
    }
    return distinctArray
}


// focus the map on cities contained in the search
function focusMap(focusCities) {
    // here is the feature group we will focus on:
    const focusGroup = new L.featureGroup()
    // Now loop through all the markers, and see if the city is in focusCities
    for (let i = 0; i < markers.length; i++) {
        makeGrayscale(markers[i].marker)
        if (focusCities.includes(markers[i].cityData['city'])) {
            markers[i].marker.addTo(focusGroup)
            removeGrayscale(markers[i].marker)
        }
    }
    map.fitBounds(focusGroup.getBounds(), {maxZoom: 5})

}


function makeGrayscale(marker) {
    marker._icon.classList.add('grayscale')
}


function removeGrayscale(marker) {
    marker._icon.classList.remove('grayscale')
}


function renderMap(cities) {
    map = L.map('map')
    let featureGroup = new L.featureGroup();
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    }).addTo(map);
    // Create an array of all of our markers for easier access.THey are global now, except in strict mode
    markers = []
    for(i = 0; i < cities.length; i++){
        let city_name = cities[i]['city'];
        let country_name = cities[i]['country']
        let marker = L.marker([cities[i]['lat'], cities[i]['long']]).addTo(map).addTo(featureGroup)
        .bindPopup(country_name +'<br>' + city_name)
        // Rather than show popup on click, simply show it on mouseover. This way when we click we can search
        .on('mouseover', function (e) {
            this.openPopup();
        })
        // Close popover on mouse out
        .on('mouseout', function (e) {
            this.closePopup();
        })
        .on("click", function(e){
            // Re-render table with AJAX
            // Clear table using DataTables.js
            let table = $('#myTable').DataTable();
            table
                .columns( 1 )
                .search( city_name )
                .draw();
        })
        // Now add to an array for easy access
        markers.push({cityData: cities[i], marker: marker})
    }
    map.fitBounds(featureGroup.getBounds(), {maxZoom: 5});
}
