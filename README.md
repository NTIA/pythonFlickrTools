# Python Flickr Tools

This project is a Python command-line tool that acts as a convenient wrapper for the flickr API and may serve as a basis for an interface between the flickr API and a "local" image database.

## Dependencies

* `wget` Python package: https://pypi.python.org/pypi/wget/
* Python Flickr API kit: http://stuvel.eu/flickrapi
* `urllib3` Python package: https://pypi.python.org/pypi/urllib3

All are available on `pip`. Use `pip install <package_name>` to install.

## flickr API Key

In order to make use of this software you will need an API key and secret. In oder to get these credentials, you need to [register an app with flickr](https://www.flickr.com/services/apps/create/). Then populate the file `apikeys.py` with the credentials and you should be off to the races.

## Usage

`usage: getFlickrImages.py [-h] [--setID SETID] [--groupNo GROUPNO]
                          [--flickrMTNS FLICKRMTNS] [--flickrMTP FLICKRMTP]
                          [--numPhotos NUMPHOTOS] [--photoSize PHOTOSIZE]
                          [--autoCull]`

`download requested images from flickr based on requested parameters.`

*  -h, --help  show this help message and exit
*  --setID SETID  specify flickr set ID. if setID is specified you may not specify a group number.
*  --groupNo GROUPNO  specify flickr set group number. if group number is specified you may not specify a setID.
*  --flickrMTNS FLICKRMTNS  specify flickr machine tag name space. if MTNS is specified, you must specify a name space predicate (flickrMTP) as well.
*  --flickrMTP FLICKRMTP  specify flickr machine tage predicate. this argument is required if a flickrMTNS is specified.
*  --numPhotos NUMPHOTOS  specify the number of images to download (or use "all" to download all available images)---default is all images
*  --photoSize PHOTOSIZE  specify the size of the image to download from flickr. valid options: `Square`, `Large_1600`, `Small_320`, `Original`, `Large`, `Medium`, `Medium_640`, `Large_Square`, `Medium_800`, `Small`, `Large_2048`, `Thumbnail`
*  --autoCull  specify whether or not to remove images from the local system if it is also removed from the server OR whether to remove images when the number of images on the local system exceeds numPhotos. Default is false.

## Legal
THE NATIONAL TELECOMMUNICATIONS AND INFORMATION ADMINISTRATION, INSTITUTE 
FOR TELECOMMUNICATION SCIENCES ("NTIA/ITS") DOES NOT MAKE ANY WARRANTY OF 
ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, 
THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, 
NON-INFRINGEMENT AND DATA ACCURACY.  THIS SOFTWARE IS PROVIDED "AS IS."  
NTIA/ITS does not warrant or make any representations regarding the use of 
the software or the results thereof, including but not limited to the 
correctness, accuracy, reliability or usefulness of the software or the 
results.

You can use, copy, modify, and redistribute the NTIA/ITS developed 
software upon your acceptance of these terms and conditions and upon your 
express agreement to provide appropriate acknowledgments of NTIA's 
ownership of and development of the software by keeping this exact text 
present in any copied or derivative works.

The user of this Software ("Collaborator") agrees to hold the U.S. 
Government harmless and indemnifies the U.S. Government for all 
liabilities, demands, damages, expenses, and losses arising out of
the use by the Collaborator, or any party acting on its behalf, of 
NTIA/ITS' Software, or out of any use, sale, or other disposition by the 
Collaborator, or others acting on its behalf, of products made
by the use of NTIA/ITS' Software.
