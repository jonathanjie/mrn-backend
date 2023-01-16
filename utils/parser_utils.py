import re

from django.contrib.gis.geos import Point
from latlon import string2latlon


def parse_dm(lat: str, lon: str) -> Point:
    lat_lon = string2latlon(lat, lon, "d%°%M%'%H")
    # parts = re.split('[^\d\w]+', dm)
    lat, lon = lat_lon.to_string("%D")
    pnt = Point(float(lat), float(lon), srid=4326)
    return pnt
# Usage: parse_dm("1°15.1'N", "103°51.1'E")
