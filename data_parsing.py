"""
The initial plan for this script is to:
- Input: NMEA sentences
- Output: A file containing a route in a format that can be integrated into a map
"""

import folium

area_map = folium.Map(location=(52.63, -8.65), zoom_start=15)

folium.GeoJson("challenge_area.json").add_to(area_map)

area_map.save("area_map.html")