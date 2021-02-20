/*
  Copyright 2017 Google Inc.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
*/

const mapStyle = [
  {"featureType": "administrative", "elementType": "labels.text.fill", "stylers": [{"color": "#444444"}]},
  {"featureType": "landscape", "elementType": "all", "stylers": [{"color": "#f2f2f2"}]},
  {"featureType": "poi", "elementType": "all", "stylers": [{"visibility": "off"}]},
  {"featureType": "poi", "elementType": "labels.icon", "stylers": [{"visibility": "off"}]},
  {"featureType": "poi.school", "elementType": "all", "stylers": [{"visibility": "on"}, {"hue": "#ff0000"}, {"gamma": "0.70"}, {"weight": "2.41"}, {"saturation": "34"}, {"lightness": "1"}]},
  {"featureType": "poi.school", "elementType": "geometry", "stylers": [{"visibility": "on"}]},
  {"featureType": "poi.school", "elementType": "labels.icon", "stylers": [{"visibility": "on"}]},
  {"featureType": "road", "elementType": "all", "stylers": [{"saturation": -100}, {"lightness": 45}]},
  {"featureType": "road", "elementType": "labels.text", "stylers": [{"weight": "1.74"}, {"visibility": "on"}]},
  {"featureType": "road", "elementType": "labels.text.fill", "stylers": [{"visibility": "on"}, {"color": "#635c5c"}]},
  {"featureType": "road.highway", "elementType": "all", "stylers": [{"visibility": "simplified"}]},
  {"featureType": "road.arterial", "elementType": "labels.icon", "stylers": [{"visibility": "off"}]},
  {"featureType": "transit", "elementType": "all", "stylers": [{"visibility": "off"}]},
  {"featureType": "water", "elementType": "all", "stylers": [{"color": "#78bdd9"}, {"visibility": "on"}]}
];

function initMap() {

  const sliders = document.querySelectorAll('.mdl-slider');
  const spinner = document.querySelector('.mdl-spinner');
  const map = new google.maps.Map(document.querySelector('#map'), {
    zoom: 14,
    center: window.mapCenter,
    styles: mapStyle
  });

  // Hide the markers rendered via map.data.loadGeoJson, since we'll add markers
  // seperately with MarkerClusterer.
  map.data.setStyle(() => ({visible: false}));

  // Info window will show a property's information when its marker is clicked.
  const infoWindow = new google.maps.InfoWindow();
  infoWindow.setOptions({pixelOffset: new google.maps.Size(0, -30)});

  var infoBubble = new InfoBubble();

  // We call map.data.loadGeoJson every time the bounds_changed event is triggered,
  // which sometimes can occur multiple times very quickly in succession, so we
  // only do this inside a function run via setTimeout, which is cancelled each
  // time the event is triggered. timeoutHandler stores the handler for this.
  let timeoutHandler = 0;

  // MarkerClusterer instance which we store to allow us to call clearMarkers
  // on it, each time the property data is received after map.data.loadGeoJson
  // being called.
  let markerCluster = null;

  // Stores the bounds used for retrieving data, so that when the bounds_changed
  // event is triggered, we don't request new data if the new bounds fall within
  // dataBounds, for example when zooming in.
  let dataBounds = null;

  // Store the last zoom value to determine if we zoomed in or not during bound change
  // events.
  let lastZoom = map.zoom;

  // Loads properties via map.data.loadGeoJson inside a setTimeout handler, which is
  // cancelled each time loadProperties is called.
  function loadProperties() {

    // Show the loading spinner.
    spinner.classList.add('is-active');

    clearTimeout(timeoutHandler);
    timeoutHandler = setTimeout(() => {

      // For retrieving data, use a larger (2x) bounds than the actual map bounds,
      // which will allow for some movement of the map, or one level of zooming
      // out, without needed to load new data.
      const ne = map.getBounds().getNorthEast();
      const sw = map.getBounds().getSouthWest();
      const extendedLat = ne.lat() - sw.lat();
      const extendedLng = ne.lng() - sw.lng();
      dataBounds = new google.maps.LatLngBounds(
        new google.maps.LatLng(sw.lat() - extendedLat, sw.lng() - extendedLng),
        new google.maps.LatLng(ne.lat() + extendedLat, ne.lng() + extendedLng)
      );

      // Build the querystring of parameters to use in the URL given to
      // map.data.loadGeoJson, which consists of the various form field
      // values and the current bounding box.
      const params = {
        ne: dataBounds.getNorthEast().toUrlValue(),
        sw: dataBounds.getSouthWest().toUrlValue()
      };
      Array.prototype.forEach.call(sliders, (item) => params[item.id] = item.value);
      const types = document.querySelectorAll('input[name="property-types"]:checked');
      params['property-types'] = Array.prototype.map.call(types, (item) => item.value).join(',');
      const on_market = document.querySelectorAll('input[name="on-market"]:checked');
      params['on-market'] = Array.prototype.map.call(on_market, (item) => item.value).join(',');
      const off_market = document.querySelectorAll('input[name="off-market"]:checked');
      params['off-market'] = Array.prototype.map.call(off_market, (item) => item.value).join(',');
      const pfc = document.querySelectorAll('input[name="pfc"]:checked');
      params['pfc'] = Array.prototype.map.call(pfc, (item) => item.value).join(',');

      const new_construction = document.querySelectorAll('input[name="new-construction"]:checked');
      params['new-construction'] = Array.prototype.map.call(new_construction, (item) => item.value).join(',');

      const vacant = document.querySelectorAll('input[name="vacant"]:checked');
      params['vacant'] = Array.prototype.map.call(vacant, (item) => item.value).join(',');
      const absentee = document.querySelectorAll('input[name="absentee"]:checked');
      params['absentee'] = Array.prototype.map.call(absentee, (item) => item.value).join(',');
      // console.log(map.zoom)
      params['zoom'] = map.zoom
      const url = window.propertiesGeoJsonUrl + '?' + Object.keys(params).map((k) => k + '=' + params[k]).join('&');



      map.data.loadGeoJson(url, null, (features) => {
        // Set the value in the "Total properties: x" text.
        document.querySelector('#total-text').innerHTML = features.length;
        // Hide the loading spinner.
        spinner.classList.remove('is-active');
        // Clear the previous marker cluster.
        if (markerCluster !== null) {
          markerCluster.clearMarkers();
        }

        // console.log(features)

        // Build an array of markers, one per property.
        const markers = features.map((feature) => {

          const marker = new google.maps.Marker({
            position: feature.getGeometry().get(0),
            icon: window.imagePath + 'marker.png'
          });

          // Show the property's details in the infowindow when
          // the marker is clicked.
          marker.addListener('click', () => {
              // alert(map.center);
              const position = feature.getGeometry().get();
              infoBubble.close();

              console.log(map.zoom);

              // tab 1: property
              var property_string = `
              <div>
                <img src="https://maps.googleapis.com/maps/api/streetview?size=300x200&location=${position.lat()},${position.lng()}&key=${window.apiKey}">
                <h5>${feature.getProperty('address')}</h5>
                <p>${feature.getProperty('description')}</p>
                <ul>


                  `;

              const price_to_rent = feature.getProperty('price_to_rent');
              if (price_to_rent) {
                property_string += `<li>Price to Rent Ratio: ${feature.getProperty('price_to_rent')}</li>`;
              }

              const price_to_rent_est_beds = feature.getProperty('price_to_rent_est_beds');
              if (price_to_rent_est_beds) {
                property_string += `<li>Price to Rent Estimate (Beds) Ratio: ${feature.getProperty('price_to_rent_est_beds')}</li>`;
              }

              const list_price = feature.getProperty('list_price');
              if (list_price) {
                property_string += `<li>List price: ${feature.getProperty('list_price')}</li>`;
              }

              const list_date = feature.getProperty('list_date');
              if (list_date) {
                property_string += `<li>List date: ${feature.getProperty('list_date')}</li>`;
              }

              const original_price = feature.getProperty('original_price');
              if (original_price) {
                property_string += `<li>Original price: ${feature.getProperty('original_price')}</li>`;
              }

              const one_cf = feature.getProperty('one_cf');
              if (one_cf) {
                property_string += `<li>One year cash flow estimate: ${feature.getProperty('one_cf')}</li>`;
              }


              const rent = feature.getProperty('rent');
              if (rent) {
                property_string += `<li>Rent: ${feature.getProperty('rent')}</li>`;
              }

              const rent_estimate_beds = feature.getProperty('rent_estimate_beds');
              if (rent_estimate_beds) {
                property_string += `<li>Rent Estimate Using Beds: ${feature.getProperty('rent_estimate_beds')}</li>`;
              }

              const rent_estimate_sqft = feature.getProperty('rent_estimate_sqft');
              if (rent_estimate_sqft) {
                property_string += `<li>Rent Estimate Using Sqft: ${feature.getProperty('rent_estimate_sqft')}</li>`;
              }

              const year_built = feature.getProperty('year_built');
              if (year_built) {
                property_string += `<li>Year Built: ${feature.getProperty('year_built')}</li>`;
              }

              const units = feature.getProperty('units');
              if (units) {
                property_string += `<li>Units: ${feature.getProperty('units')}</li>`;
              }

              const zoning = feature.getProperty('zoning');
              if (zoning) {
                property_string += `<li>Zoning: ${feature.getProperty('zoning')}</li>`;
              }

              const lot_size = feature.getProperty('lot_size');
              if (lot_size) {
                property_string += `<li>Lot Size: ${feature.getProperty('lot_size')} sq ft</li>`;
              }

              const new_build = feature.getProperty('new_build');
              if (new_build) {
                property_string += `<li>New build</li>`;
              }

              const nb_type = feature.getProperty('nb_type');
              if (nb_type) {
                property_string += `<li>New build type: ${feature.getProperty('nb_type')}</li>`;
              }

              const bedrooms = feature.getProperty('bedrooms');
              if (bedrooms) {
                property_string += `<li>Bedrooms: ${feature.getProperty('bedrooms')}</li>`;
              }

              const sqft = feature.getProperty('sqft');
              if (sqft) {
                property_string += `<li>Sqft: ${feature.getProperty('sqft')}</li>`;
              }

              const bathrooms = feature.getProperty('bathrooms');
              if (bathrooms) {
                property_string += `<li>Bathrooms: ${feature.getProperty('bathrooms')}</li>`;
              }

              const taxes = feature.getProperty('taxes');
              if (taxes) {
                property_string += `<li>Taxes: ${feature.getProperty('taxes')}</li>`;
              }


              property_string += '</ul></div>';


              // tab 2: demographics
              var demographics_string = `
              <div>
                <h5>${feature.getProperty('address')}</h5>
                <p>${feature.getProperty('description')}</p>
                <ul>


                  `;
              const growth_1 = feature.getProperty('growth_1');
              if (growth_1) {
                demographics_string += `<li>1yr Population Growth: ${feature.getProperty('growth_1')}</li>`;
              }

              const growth_3 = feature.getProperty('growth_3');
              if (growth_3) {
                demographics_string += `<li>3yr Population Growth: ${feature.getProperty('growth_3')}</li>`;
              }

              const growth_5 = feature.getProperty('growth_5');
              if (growth_5) {
                demographics_string += `<li>5yr Population Growth: ${feature.getProperty('growth_5')}</li>`;
              }

              const unemployed = feature.getProperty('unemployed');
              if (unemployed) {
                demographics_string += `<li>Percentage Unemployed: ${feature.getProperty('unemployed')}%</li>`;
              }

              const college = feature.getProperty('college');
              if (college) {
                demographics_string += `<li>Percentage in College: ${feature.getProperty('college')}%</li>`;
              }

              const vacancy = feature.getProperty('vacancy');
              if (vacancy) {
                demographics_string += `<li>Percentage Vacant: ${feature.getProperty('vacancy')}%</li>`;
              }

              const family = feature.getProperty('family');
              if (family) {
                demographics_string += `<li>Percentage Family: ${feature.getProperty('family')}%</li>`;
              }

              demographics_string += '</ul></div>';


              // tab 2: demographics
              // var demographics_string = `
              // <div>
              //   <h5>${feature.getProperty('address')}</h5>
              //   <p>${feature.getProperty('description')}</p>
              //   <ul>
              //
              //
              //     `;
              //
              // const family = feature.getProperty('family');
              // if (family) {
              //   demographics_string += `<li>Percentage Family: ${feature.getProperty('family')}%</li>`;
              // }
              //
              // demographics_string += '</ul></div>';

              // tab 3: demographics
              var transactions_string = `
              <div>
                <p>${feature.getProperty('description')}</p>
                <ul>


                  `;

              const transactions = feature.getProperty('transactions');
              if (transactions) {
                transactions_string += `<li>Transaction dump: ${feature.getProperty('transactions')}</li>`;
              }

              transactions_string += '</ul></div>';


              var motivation_string = `
              <div>
                <p>${feature.getProperty('description')}</p>
                <ul>


                  `;

              const pfc = feature.getProperty('pfc');
              if (pfc) {
                motivation_string += `<li>Foreclosure filed</li>`;
              }

              const pfc_owner = feature.getProperty('pfc_owner');
              if (pfc_owner) {
                motivation_string += `<li>Owner at filing: ${feature.getProperty('pfc_owner')}</li>`;
              }

              const pfc_date = feature.getProperty('pfc_date');
              if (pfc_date) {
                motivation_string += `<li>Date filed: ${feature.getProperty('pfc_date')}</li>`;
              }

              const absent_owner = feature.getProperty('absent_owner');
              if (absent_owner) {
                motivation_string += `<li>Absent owner: ${feature.getProperty('absent_owner')}</li>`;
              }

              const absent_owner_mail = feature.getProperty('absent_owner_mail');
              if (absent_owner_mail) {
                motivation_string += `<li>Absent owner address: <br>
                ${feature.getProperty('absent_owner_mail')} <br>
                ${feature.getProperty('absent_owner_city')} ${feature.getProperty('absent_owner_state')}, ${feature.getProperty('absent_owner_zip')}</li>`;
              }

              const vacant_owner = feature.getProperty('vacant_owner');
              if (vacant_owner) {
                motivation_string += `<li>Vacant owner: ${feature.getProperty('vacant_owner')}</li>`;
              }

              const vacant_owner_mail = feature.getProperty('vacant_owner_mail');
              if (vacant_owner_mail) {
                motivation_string += `<li>Vacant owner address: <br>
                ${feature.getProperty('vacant_owner_mail')} <br>
                ${feature.getProperty('vacant_owner_city')} ${feature.getProperty('vacant_owner_state')}, ${feature.getProperty('vacant_owner_zip')}</li>`;
              }


              motivation_string += '</ul></div>';


             // alert(marker.position);

             infoBubble = new InfoBubble({
               // map: map,
               // position: marker.position,
               content: '<div class="phoneytext">Some label</div>',
               shadowStyle: 1,
               padding: 2,
               borderRadius: 4,
               arrowSize: 10,
               borderWidth: 1,
               maxHeight: 350,
               maxWidth: 300,
               backgroundClassName: 'phoney'
             });

             infoBubble.addTab('Property', property_string);
             infoBubble.addTab('Demographics', demographics_string);
             infoBubble.addTab('Transactions', transactions_string);
             infoBubble.addTab('Motivation', motivation_string)
             infoBubble.open(map,marker);

          });

          return marker;
        });

        // Build the marker clusterer.
        markerCluster = new MarkerClusterer(map, markers, {
          styles: [1, 2, 3].map(i => ({
            url: window.imagePath + `cluster${i}.png`,
            width: 24+(24*i),
            height: 24+(24*i),
            textColor: '#fff',
            textSize: 12+(4*i)
          }))
        });
      });

    }, 100);
  }

  // Refresh data each time the map bounds change, and fall outside the
  // bounds of currently loaded data.
  google.maps.event.addListener(map, 'bounds_changed', () => {
    zoomed_in = (map.zoom >= 17 && lastZoom < 17)
    if (dataBounds === null ||
          !dataBounds.contains(map.getBounds().getNorthEast()) ||
          !dataBounds.contains(map.getBounds().getSouthWest()) ||
        zoomed_in) {
      loadProperties();
    }
    lastZoom = map.zoom
  });

  // Refresh data each time one of the sliders change.
  Array.prototype.forEach.call(sliders, item =>
    item.addEventListener('input', () => {
      loadProperties();
      // Also update the slider's text.
      let value = Number(item.value);
      if (item.id.indexOf('nearest') === 0) {
        value = value === 1 ? 'Any' : (value-1) + 'km';
      }
      document.querySelector(`#${item.id}-text`).innerHTML = value;
    })
  );

  // Refresh data when the "property types" checkboxes change.
  const types = document.querySelectorAll('input[name="property-types"]');
  Array.prototype.forEach.call(types, item => item.addEventListener('change', loadProperties));

  // Refresh data when the "property types" checkboxes change.
  const on_market = document.querySelectorAll('input[name="on-market"]');
  Array.prototype.forEach.call(on_market, item => item.addEventListener('change', loadProperties));

  const off_market = document.querySelectorAll('input[name="off-market"]');
  Array.prototype.forEach.call(off_market, item => item.addEventListener('change', loadProperties));

  const pfc = document.querySelectorAll('input[name="pfc"]');
  Array.prototype.forEach.call(pfc, item => item.addEventListener('change', loadProperties));

  const new_construction = document.querySelectorAll('input[name="new-construction"]');
  Array.prototype.forEach.call(new_construction, item => item.addEventListener('change', loadProperties));

  const vacant = document.querySelectorAll('input[name="vacant"]');
  Array.prototype.forEach.call(vacant, item => item.addEventListener('change', loadProperties));

  const absentee = document.querySelectorAll('input[name="absentee"]');
  Array.prototype.forEach.call(absentee, item => item.addEventListener('change', loadProperties));

}
