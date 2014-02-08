import logging
import os
import bottle
import json
import urllib2
try:
  from cStringIO import StringIO
except:
  from StringIO import StringIO
import zipfile
import uuid
import json

# Azure libraries
from azure.storage import *

# Bottle libraries
from bottle import route, template, request, redirect, static_file


class GeodataToBlobstorage():
     """ 
     save geodata files to an Azure BlobStorage and return the public URL.
     """

     def __init__(self):
          self.config = {
               "account_name"    : "ping13",
               "container"       : "send2geoadmin",
          }
          self.config['url'] = "http://%s.blob.core.windows.net/%s" % (self.config['account_name'], self.config['container'])
          # get the storage access key from an environmant variable
          # (This can be set in Azure's management portal)
          try:
               self.config['access_key'] = os.environ['APPSETTING_storage_access_key']
          except:
               logging.error("Whoops, there is no storage key defined")
               raise 
          self.geojson2kml_url = "http://geojson2kml.azurewebsites.net/convert"

          self.blob_service = BlobService(account_name= self.config['account_name'], 
                                          account_key= self.config['access_key'])

     def upload_geojson(self,geojson_data):
          req = urllib2.Request(self.geojson2kml_url, 
                                geojson_data, {'Content-Type': 'application/json'})
          f = urllib2.urlopen(req)
          data = json.loads(f.read())
          f.close()
          return self._save_as_blobstorage(data['kml'], "doc_from_geojson.kml")

     def upload_kmz(self,kmz_data):
          """Take the KMZ data and store the KML file in the Azure
          BlobStorage. Returns the URL of the blob.
          """     
          # unzip the kmz data and find the .kml-file
          logging.debug("Start unzip")
          fp = StringIO(kmz_data)
          try:
               zf = zipfile.ZipFile(fp,"r")
          except Exception, e:
               logging.error("Problem with the zipfile: %s" % str(e))
               raise

          logging.debug("Done with unzip.")
          docname = None

          for name in  zf.namelist():
               if name.endswith(".kml"):
                    docname = name
          if docname == None:
               return None
          logging.debug("Found %s" % docname)
          
          return self._save_as_blobstorage(zf.read(docname), "doc.kml")

     def _save_as_blobstorage(self,blob, blobname):
          # store the contents of the KML file in Azure's blob storage
          blobdirname = str(uuid.uuid4())
          fullblobname = "%s/%s" % (blobdirname, blobname)
          self.blob_service.put_blob(self.config['container'], fullblobname , blob, 
                                     x_ms_blob_type='BlockBlob', 
                                     x_ms_blob_content_type = "application/vnd.google-earth.kml+xml")
          url = "%s/%s" % (self.config['url'],fullblobname)
          logging.debug("URL %s" % url)
          return url

@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static/')

@route('/')
def index():                                                                     
     error_message = request.query.error
     return template('home',error_message=error_message)


@route('/upload_kmz', method='POST')
def do_upload():
     try:
          upload = request.files.get('upload')
     except Exception, e:
          return "Error trying to get request %s" % e

     # check the extension
     name, ext = os.path.splitext(upload.filename)
     if ext not in ('.kmz','.json'):
          return './?error=File extension "%s" not allowed.' % ext

     contents = upload.file.read() 
     
     # store the the KML content in a blob on Azure and redirect 
     g2b = GeodataToBlobstorage()
     bloburl = None
     if ext == '.kmz':
          bloburl = g2b.upload_kmz(contents)
     elif ext == '.json':
          bloburl = g2b.upload_geojson(contents)

     if bloburl:
          redirect_url = "http://map.geo.admin.ch/?layers=KML||%s" % bloburl
          logging.debug("Redirect URL %s" % redirect_url)
          return redirect_url
               
     return "./?error=Whoops, something went wrong..."

app = bottle.app()

if __name__ == '__main__':
     logging.basicConfig(level=logging.DEBUG)
     bottle.run(reloader=True)
