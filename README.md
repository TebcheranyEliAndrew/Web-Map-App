# MapApp - Interactive Location Mapping Tool

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)

MapApp is a web application built with Flask that allows users to visualize locations on an interactive map, calculate distances between points, and display connection lines with distance markers.

## Features

- **Location Visualization**: Display any two locations on an interactive Folium map
- **Distance Calculation**: Automatically calculates and displays the distance between points in kilometers
- **Custom Markers**: Color-coded markers for each location
- **Connection Lines**: Optional line between locations with midpoint distance marker
- **Access Logging**: Tracks device access information including IP and user agent
- **Responsive Design**: Works on both desktop and mobile devices

## Requirements

- Python 3.7+
- Flask 2.0+
- geopy
- folium
