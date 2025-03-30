let map;

const position = { lat: 55.602090037866, lng: 11.963126490088002 };

async function initMap() {
  const { Map } = await google.maps.importLibrary("maps");
  const { AdvancedMarkerElement, PinElement } = await google.maps.importLibrary("marker");

map = new Map(document.getElementById("map"), {
    center: position,
    zoom: 16,
    mapId: "LEJRE_FITNESS",
    mapTypeId: "hybrid" // Set map type to satellite
});

// Create an info window with navigation option
const infoWindow = new google.maps.InfoWindow({
    content: `
        <div>            
            <a href="https://www.google.com/maps/dir/?api=1&destination=55.602090037866,11.962926490088002" target="_blank">
                Naviger til Lejre Fitness
            </a>
        </div>
    `
});

// Add click event listener to the marker
const parser = new DOMParser();
// A marker with a custom inline SVG.
const pinSvgString =
    '<svg xmlns="http://www.w3.org/2000/svg" width="40" height="56" viewBox="0 0 40 56" fill="none">' +
    '<path d="M20 0C10.5 0 3 7.5 3 17C3 29.5 20 56 20 56C20 56 37 29.5 37 17C37 7.5 29.5 0 20 0Z" fill="#00FF00" />' +
    '<circle cx="20" cy="17" r="10" fill="white" opacity="0.8"/>' +
    '<g transform="translate(10,9)">' +
    '  <line x1="5" y1="8" x2="15" y2="8" stroke="black" stroke-width="2.5" stroke-linecap="round"/>' +
    '  <line x1="6" y1="5" x2="6" y2="11" stroke="black" stroke-width="2.5" stroke-linecap="round"/>' +
    '  <line x1="14" y1="5" x2="14" y2="11" stroke="black" stroke-width="2.5" stroke-linecap="round"/>' +
    '  <circle cx="6" cy="8" r="3" fill="black"/>' +
    '  <circle cx="14" cy="8" r="3" fill="black"/>' +
    '</g>' +
    '</svg>';
const pinSvg = parser.parseFromString(
  pinSvgString,
  "image/svg+xml",
).documentElement;
// Create a container for the pin and label
const markerContent = document.createElement('div');
markerContent.style.display = 'flex';
markerContent.style.alignItems = 'center';
markerContent.style.gap = '5px';

// Add the SVG pin to the container
markerContent.appendChild(pinSvg);

// Create the text label
const label = document.createElement('div');
label.textContent = 'Lejre Fitness';
label.style.color = 'white';
label.style.backgroundColor = 'rgba(28, 167, 15, 0.7)';
label.style.padding = '4px 8px';
label.style.borderRadius = '4px';
label.style.fontSize = '14px';
label.style.fontWeight = 'bold';
markerContent.appendChild(label);

const pinSvgMarkerView = new AdvancedMarkerElement({
    map,
    position: position,
    content: markerContent,
    title: "Lejre Fitness",
    gmpClickable: true,
});
// Add click event listener to the marker
pinSvgMarkerView.addListener("gmp-click", ({ domEvent, latLng }) => {
    const { target } = domEvent;
  
    infoWindow.close();
    
    infoWindow.open(pinSvgMarkerView.map, pinSvgMarkerView);
  });

}

initMap();

