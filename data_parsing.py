"""
The function of this script:
- Input: NMEA sentences
- Output: A file containing a route in a format that can be integrated into a
          map.

The Arduino system will gather GPS coordinates on a journey and save them to a
txt file. This file can then be passed into this script as an input, it will
generate geojson files which then will be used to plot the journeys on the
chosen map. The map area can be generated using a geojson online editor.
"""

import json
import os
import folium


def nmea_to_decimal(value, direction):
    """
    Converts NMEA DDMM.mmmm format to Decimal Degrees (DD.dddd).
    """

    try:
        # Find the decimal point to separate degrees and minutes appropriately
        if '.' in value:
            split_index = value.find('.') - 2
        else:
            split_index = len(value) - 2

        degrees = float(value[:split_index])
        minutes = float(value[split_index:])

        decimal_degrees = degrees + (minutes / 60.0)

        # Apply negative sign for South and West
        if direction.upper() in ['S', 'W']:
            decimal_degrees = -decimal_degrees

        return decimal_degrees
    except ValueError:
        return None


def convert_gprmc_to_geojson(input_file, output_file):
    """
    This method takes an input file and a name for an output file
    """

    coordinates = []

    try:
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()

                # We only care about $GPRMC lines
                if not line.startswith('$GPRMC'):
                    continue

                parts = line.split(',')

                # Check if the line is well-formed (at least enough fields)
                if len(parts) < 12:
                    continue

                status = parts[2]

                # Only process valid GPS fixes
                if status == 'A':
                    lat_raw = parts[3]  # [3] Latitude
                    lat_dir = parts[4]  # [4] N/S
                    lon_raw = parts[5]  # [5] Longitude
                    lon_dir = parts[6]  # [6] E/W

                    lat = nmea_to_decimal(lat_raw, lat_dir)
                    lon = nmea_to_decimal(lon_raw, lon_dir)

                    if lat is not None and lon is not None:
                        # GeoJSON format requires [Longitude, Latitude]
                        coordinates.append([lon, lat])

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
        return

    # Construct the GeoJSON FeatureCollection
    geojson_output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "source": "GPRMC Data",
                    "point_count": len(coordinates)
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                }
            }
        ]
    }

    # Write to file
    with open(output_file, 'w') as f:
        json.dump(geojson_output, f, indent=4)

    print("Parsed GPS file successfuly.")


# Convert each GPS journey file into .geojson
for file in os.listdir("journeys_gps"):
    if file == ".gitignore":
        continue
    output_file_name = os.path.splitext(file)[0] + ".geojson"
    convert_gprmc_to_geojson(file, output_file_name)

# Set map load location and zoom level
area_map = folium.Map(location=(52.63, -8.65), zoom_start=15)

# Draw the challenge area
folium.GeoJson("challenge_area.geojson",
               style_function=lambda feature: {
                    'fillColor': 'lightblue',
                    'color': 'black',      # Border color
                    'weight': 2,           # Border weight
                    'fillOpacity': 0.3,    # Polygon opacity
                    'opacity': 1.0         # Border opacity
               }).add_to(area_map)

# Add all .geojson journeys to the map
for file in os.listdir("journeys_geojson"):
    if file == ".gitignore":
        continue
    folium.GeoJson("journeys_geojson/" + file, opacity=0.5).add_to(area_map)

# Save map file
area_map.save("area_map.html")
