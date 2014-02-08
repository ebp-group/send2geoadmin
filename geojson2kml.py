# This is just a test file for the conversion from geojson to KML

import urllib
import urllib2
import sys
import json


def geojson2kml(filename):
    
    url = "http://geojson2kml.azurewebsites.net/convert"
    with open(filename) as jsonfile:
        data = jsonfile.read()
        req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
        f = urllib2.urlopen(req)
        data = json.loads(f.read())
        f.close()
        return data['kml']
                     
if __name__ == "__main__":
    filename = sys.argv[1]
    print geojson2kml(filename)
