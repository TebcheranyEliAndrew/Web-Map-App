from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import folium
from datetime import datetime
import logging

class MapApp:
    def __init__(self):
        self.app = Flask(__name__)
        self.geolocator = Nominatim(user_agent="my_map_app")
        self.setup_routes()
        
    def setup_routes(self):
        @self.app.route('/', methods=['GET', 'POST'])
        def map_viewer():
            return self.handle_map_request()

    def log_access(self):
        """Log device access information"""
        ip = request.remote_addr
        device = request.headers.get('User-Agent', 'Unknown device')
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"\n[{time}] Device connected\nIP: {ip}, Device: {device}\n"
        
        assert isinstance(ip, str), "IP address must be a string"
        assert isinstance(device, str), "Device info must be a string"
        
        try:
            with open("logs.txt", 'a') as file:
                file.write(log_entry)
        except IOError as e:
            logging.error(f"Failed to write log: {e}")

    def get_location_coordinates(self, location_name):
        """Get coordinates for a location name with error handling"""
        assert location_name is not None, "Location name cannot be None"
        
        if not location_name:
            return None
            
        location = self.geolocator.geocode(location_name)
        assert location is None or hasattr(location, 'latitude') and hasattr(location, 'longitude'), \
            "Geocoding result must have latitude and longitude attributes"
        return (location.latitude, location.longitude) if location else None

    def create_base_map(self):
        """Create a base Folium map"""
        map_obj = folium.Map(location=[0, 0], zoom_start=2, tiles='cartodbpositron')
        assert isinstance(map_obj, folium.Map), "Failed to create Folium map"
        return map_obj

    def add_marker(self, map_obj, coords, popup_text, color='blue'):
        """Add a marker to the map"""
        assert isinstance(map_obj, folium.Map), "map_obj must be a Folium Map"
        assert isinstance(coords, (list, tuple)) and len(coords) == 2, \
            "Coordinates must be a list/tuple of (lat, lng)"
        assert all(isinstance(c, (int, float)) for c in coords), \
            "Coordinates must be numbers"
        assert isinstance(popup_text, str), "Popup text must be a string"
        assert color in ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                        'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
                        'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen', 
                        'gray', 'black', 'lightgray'], "Invalid color value"
        
        marker = folium.Marker(
            coords,
            popup=popup_text,
            icon=folium.Icon(color=color)
        )
        marker.add_to(map_obj)

    def add_distance_line(self, map_obj, coords1, coords2, distance):
        """Add a line between two points with distance marker"""
        assert isinstance(map_obj, folium.Map), "map_obj must be a Folium Map"
        assert all(isinstance(c, (list, tuple)) and len(c) == 2 for c in [coords1, coords2]), \
            "Both coordinates must be (lat, lng) pairs"
        assert all(isinstance(coord, (int, float)) for coord in coords1 + coords2), \
            "All coordinate values must be numbers"
        assert isinstance(distance, (int, float)) and distance >= 0, \
            "Distance must be a non-negative number"
        
        line = folium.PolyLine(
            locations=[coords1, coords2],
            color='green',
            weight=2,
            dash_array='5, 5'
        )
        line.add_to(map_obj)
        
        midpoint = [
            (coords1[0] + coords2[0]) / 2,
            (coords1[1] + coords2[1]) / 2
        ]
        assert all(isinstance(c, (int, float)) for c in midpoint), \
            "Midpoint calculation failed - invalid coordinates"
            
        marker = folium.Marker(
            midpoint,
            popup=f"Distance: {distance} km",
            icon=folium.DivIcon(html=f"""<div style="font-size: 12pt; color: black">{distance} km</div>""")
        )
        marker.add_to(map_obj)

    def calculate_distance(self, coords1, coords2):
        """Calculate distance between two coordinates in km"""
        assert coords1 is not None and coords2 is not None, "Both coordinates must be provided"
        assert all(isinstance(c, (list, tuple)) and len(c) == 2 for c in [coords1, coords2]), \
            "Coordinates must be (lat, lng) pairs"
        assert all(isinstance(coord, (int, float)) for coord in coords1 + coords2), \
            "All coordinate values must be numbers"
            
        distance = geodesic(coords1, coords2).km
        assert isinstance(distance, float) and distance >= 0, \
            "Distance calculation failed - invalid result"
        return round(distance, 2)

    def handle_map_request(self):
        """Handle the map request (GET or POST)"""
        assert hasattr(request, 'method'), "Invalid request object"
        assert request.method in ['GET', 'POST'], "Invalid HTTP method"
        
        self.log_access()
        
        if request.method == 'POST':
            return self.handle_post_request()
        return render_template('map.html')

    def handle_post_request(self):
        """Handle POST request with location data"""
        assert request.method == 'POST', "This method should only handle POST requests"
        
        location_name1 = request.form.get('location1', '').strip()
        location_name2 = request.form.get('location2', '').strip()
        show_line = 'show_line' in request.form
        
        assert isinstance(location_name1, str) and isinstance(location_name2, str), \
            "Location names must be strings"
        assert isinstance(show_line, bool), "show_line must be a boolean"
        
        m = self.create_base_map()
        locations_found = False
        distance_km = None
        coords1 = self.get_location_coordinates(location_name1) if location_name1 else None
        coords2 = self.get_location_coordinates(location_name2) if location_name2 else None
        
        # Handle location 1
        if coords1:
            self.add_marker(m, coords1, f"Location 1: {location_name1}", 'blue')
            locations_found = True
            if not coords2:  # Center map if only one location
                m.location = coords1
                m.zoom_start = 15
        
        # Handle location 2
        if coords2:
            self.add_marker(m, coords2, f"Location 2: {location_name2}", 'red')
            locations_found = True
            if coords1:  # Fit both locations if available
                m.fit_bounds([coords1, coords2])
            else:  # Center map if only one location
                m.location = coords2
                m.zoom_start = 15
        
        # Handle distance line if requested
        if show_line and coords1 and coords2:
            distance_km = self.calculate_distance(coords1, coords2)
            self.add_distance_line(m, coords1, coords2, distance_km)
        
        if locations_found:
            map_html = m._repr_html_()
            assert isinstance(map_html, str), "Map HTML generation failed"
            return render_template('map.html', 
                                map_html=map_html,
                                location1=location_name1,
                                location2=location_name2,
                                distance=distance_km,
                                show_line=show_line)
        
        return render_template('map.html', error="No locations found")

    def run(self, host='0.0.0.0', port=5000, debug=True):
        """Run the Flask application"""
        assert isinstance(host, str), "Host must be a string"
        assert isinstance(port, int) and 0 < port <= 65535, "Invalid port number"
        assert isinstance(debug, bool), "Debug must be a boolean"
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    app = MapApp()
    app.run()