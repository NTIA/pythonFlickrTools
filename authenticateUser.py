import flickrapi
from apikeys import *

flickr = flickrapi.FlickrAPI(flickrKey, flickrSecret)
flickr.authenticate_via_browser(perms='read')