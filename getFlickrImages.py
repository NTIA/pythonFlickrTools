import flickrapi
import wget
from os import path, walk, remove
from sys import exit, argv
import json
from argparse import ArgumentParser
from apikeys import *
# use a modern url library to ensure proper SSL connections
import urllib3

# instantiate a flickrAPI object that will give us results in user-friendly JSON
flickr = flickrapi.FlickrAPI(flickrKey, flickrSecret, cache=True, format='parsed-json')
if not flickr.token_valid(perms='read'):
  print "operating unauthenticated, may not have permission to see all images"
# but not all the functions we need are available in JSON, so here's another object :/
flickrEtree = flickrapi.FlickrAPI(flickrKey, flickrSecret, cache=True)

class picinfo(object):
  """This class will store information about images on flickr."""
  picoutdir = 'images'
  def __init__(self,flickrSpec,photosetInfo,photoSize = 'Large'):
    self.photo_size = photoSize
    self.photosetInfo = photosetInfo
    self.flickrSpec = flickrSpec
    self.sourceUrls = self.urlMaker()
    self.filename = self.picoutdir + '/' + self.fnameMaker()
    self.flickrID = flickrSpec['id']
    if path.isfile(self.filename):
      self.localFileExists = True
    else:
      deets = flickr.photos_getInfo(photo_id=flickrSpec['id'])
      self.date = deets['photo']['dates']['posted']
      self.title = deets['photo']['title']['_content']
      self.description = deets['photo']['description']['_content']
      self.url = deets['photo']['urls']['url'][0]['_content']
      self.tags = self.getTags(deets)
      self.mTags = self.getMachineTags(deets)
      self.localFileExists = False
      # self.write2file()
  def urlMaker(self):
    sizes = flickr.photos_getSizes(photo_id=self.flickrSpec['id'])
    out_dict = {}
    for loopdict in sizes['sizes']['size']:
      out_dict[loopdict['label']] = loopdict['source']
    return out_dict
  def fnameMaker(self):
    # the following is hack until I figure out how to deal with videos
    try:
      urlstub, fname = path.split(self.sourceUrls[self.photo_size])
    except:
      urlstub, fname = path.split(self.sourceUrls['Large Square'])
    return fname
  def getTags(self,photoDetails):
    allTags = []
    for items in photoDetails['photo']['tags']['tag']:
      if items['machine_tag'] == 0:
        allTags.append(items['raw'])
    return allTags
  def getMachineTags(self,photoDetails):
    allTags = []
    for items in photoDetails['photo']['tags']['tag']:
      if items['machine_tag'] == 1:
        allTags.append(items['raw'])
    return allTags
  def downloadPhoto(self):
    # the following is hack until I figure out how to properly deal with videos
    print self.sourceUrls[self.photo_size] + "\r"
    try: 
      wget.download(self.sourceUrls[self.photo_size],self.picoutdir)
      print "\r"
      urlstub, fname = path.split(self.sourceUrls[self.photo_size])
      self.localFileExists = True
      return self.picoutdir + "/" + fname
    except:
      wget.download(self.sourceUrls['Large Square'],self.picoutdir)
      print "\r"
      urlstub, fname = path.split(self.sourceUrls['Large Square'])
      self.localFileExists = True
      return self.picoutdir + "/" + fname
  def downloadOriginal(self):
    wget.download(self.sourceUrls['Original'],self.picoutdir)
    print "\r"
    urlstub, fname = path.split(self.sourceUrls['Original'])
    self.localFileExists = True
    return self.picoutdir + "/" + fname
  def write2file(self):
    fileoutdir = 'im-info/'
    filename = ''
    saveThese = vars(self)
    splitpath = path.split(self.filename)
    splitfname = path.splitext(splitpath[1])
    jsonFname = fileoutdir + splitfname[0] + '.json'
    with open(jsonFname, "w") as outfile:
      json.dump(saveThese,outfile)

def flickrSetSearch(dct):
  """this function returns all images in a set in the order specified by the set"""
  photStruct = dict(enumerate(flickrEtree.walk_set(photoset_id=dct['set'])))
  useful = []
  for ind in range(0, len(photStruct)):
    useful.append({'farmid': photStruct[ind].get('farm'),
    'serverid': photStruct[ind].get('server'),
    'id': photStruct[ind].get('id'),
    'secret': photStruct[ind].get('secret'),
    'title': photStruct[ind].get('title')})
  return useful, photStruct

def flickrGroupSearch(dct):
  """this function returns images from a group with no guaranteed order."""
  photStruct = dict(enumerate(flickrEtree.walk(group_id=dct['groupNo'],sort=dct['sort'],per_page=500)))
  useful = []
  for ind in range(0, len(photStruct)):
    useful.append({'farmid': photStruct[ind].get('farm'),
    'serverid': photStruct[ind].get('server'),
    'id': photStruct[ind].get('id'),
    'secret': photStruct[ind].get('secret'),
    'title': photStruct[ind].get('title')})
  return useful, photStruct

# this funtion takes in a pic info object, loops through it, and creates two 
# output variables, a dict that translates an upload date to a flickr id, and a 
# list that has all upload dates sorted newest to oldest.
def wrangleDates(dictOfPics, dateList, dateTranslator,clobber):
  if clobber:
    dateList = []
    dateTranslator = {}
  for phootID in dictOfPics:
    if not 'date' in dictOfPics[phootID]:
      print "if you're seeing this, the following printout should be missing a 'date' key:"
      print dictOfPics[phootID]
    else:
      dateList.append(int(dictOfPics[phootID]['date']))
      dateTranslator[int(dictOfPics[phootID]['date'])] = int(phootID)
  dateList.sort(reverse=False)
  return dateList, dateTranslator

if __name__ == "__main__":
  # set up some argument parsing i guess
  parser = ArgumentParser(description="download requested images from flickr based on " 
  "requested parameters.")
  parser.add_argument('--setID', help="specify flickr set ID. if setID is specified you may not specify a group number.")
  parser.add_argument('--groupNo', help="specify flickr set group number. if group number is specified you may not specify a setID.")
  parser.add_argument('--flickrMTNS', help="specify flickr machine tag name space. if MTNS is specified, you must specify a name space predicate (flickrMTP) as well.")
  parser.add_argument('--flickrMTP', help="specify flickr machine tage predicate. this argument is required if a flickrMTNS is specified.")
  parser.add_argument('--numPhotos', type=int, help="specify the number of images to download (or use \"all\" to download all available images)---default is all images")
  parser.add_argument('--photoSize', help="specify the size of the image to download from flickr. valid options: Square, Large_1600, Small_320, Original, Large, Medium, Medium_640, Large_Square, Medium_800, Small, Large_2048, Thumbnail")
  parser.add_argument('--autoCull', action='store_true', help="specify whether or not to remove images from the local system if it is also removed from the server OR whether to remove images when the number of images on the local system exceeds numPhotos. Default is false.")
  if len(argv) == 1:
    parser.print_help()
    print "must specify either setID or groupNo at the minimum."
    exit(1)
  args = parser.parse_args()
  
  
  setdeets = {}
  searchopts = {}
  infoFname = ''
  
  if args.setID:
    setdeets['set'] = args.setID
    searchopts['set'] = args.setID
    infoFname = infoFname + "setNo_" + setdeets['set']
    setinfo = flickr.photosets_getInfo(photoset_id=setdeets['set'])
    setdeets['title'] = setinfo['photoset']['title']['_content']
    setdeets['description'] = setinfo['photoset']['description']['_content']
  else:
    setdeets['set'] = ''
  
  if args.groupNo:
    setdeets['groupNo'] = args.groupNo
    searchopts['groupNo'] = args.groupNo
    groupInfo = flickr.groups_getInfo(group_id=setdeets['groupNo'])
    setdeets['groupTitle'] = groupInfo['group']['name']['_content']
    setdeets['groupDesc'] = groupInfo['group']['description']['_content']
    infoFname = infoFname + "groupNo_" + setdeets['groupNo']
  else:
    setdeets['groupNo'] = ''
  
  if args.flickrMTNS:
    flickrMTNS = args.flickrMTNS
    if args.flickrMTP:
      flickrMTP = args.flickrMTP
      infoFname = infoFname + '_' + flickrMTNS + '_' + flickrMTP
    else:
      parser.print_help()
      print "if a flickrMTNS is specified a flickrMTP must be specified as well."
      exit(1)
  else:
    flickrMTNS = '';
  
  if args.numPhotos:
    searchopts['numPhotos'] = args.numPhotos
  else:
    searchopts['numPhotos'] = 'all';
  
  if args.photoSize:
    searchopts['photoSize'] = args.photoSize.replace("_", " ")
  else:
    searchopts['photoSize'] = 'Large'
  
  if args.autoCull:
    searchopts['autoCull'] = True;
  else:
    searchopts['autoCull'] = False;
  
  searchopts['sort'] = 'date-posted-asc'
  infoFname = infoFname + '.json'
  print infoFname
  
  # let's see what information we already have about this particular search.
  if path.isfile(infoFname):
    # read it in
    print "parsing existing info"
    with open(infoFname,'r') as f:
      allPhotoInfo = json.load(f)
    photosInfo = allPhotoInfo['photosInfoDict']
    dateList = allPhotoInfo['sortedDates']
    dateTranslator = allPhotoInfo['dateTranslator']
    if flickrMTNS:
      if not 'mTagGroupsDict' in allPhotoInfo:
        mTagGroups = {}
      else:
        mTagGroups = allPhotoInfo['mTagGroupsDict']
    else:
      mTagGroups = allPhotoInfo['mTagGroupsDict']
  else:
    # set up the variables we'll need
    photosInfo = {}
    dateList = []
    dateTranslator = {}
    mTagGroups = {}
  
  # now do the actual flickr search
  if (('set' in searchopts) and ('groupNo' in searchopts)):
    parser.print_help()
    print "cannot specify both setID and groupNo."
    exit(1)
  elif 'set' in searchopts:
    outPhots, fullStruct = flickrSetSearch(searchopts)
    print "accessible photos in this set = " + str(len(outPhots))
  elif 'groupNo' in searchopts:
    outPhots, fullStruct = flickrGroupSearch(searchopts)
    print "accessible photos in this group = " + str(len(outPhots))
    #outPhots.reverse()
  
  # if the settings dictate to download all the photos, make a list that says so
  if searchopts['numPhotos'] == 'all':
    dl_list = outPhots
  else:
    # otherwise trim that list to only the most recent x photos
    dl_list = outPhots[-int(searchopts['numPhotos']):]
  
  # need to figure out what images we already have set information for in the 
  # photosInfo var (that is either empty or was read from disk)
  picinfoList = []
  idList = []
  # download only the photos we need to download
  for record in dl_list:
    thisPhootID = record['id']
    
    # if we've already got info for this photo
    if thisPhootID in photosInfo:
      pass
    else:
      # otherwise, get info about it and add it to our list.
      picinfoList.append(picinfo(record,setdeets,searchopts['photoSize']))
      photosInfo[thisPhootID] = vars(picinfoList[-1])
      # get information about upload dates and upload dates with respect to flickr IDs
      dateList, dateTranslator = wrangleDates(photosInfo, dateList, dateTranslator, True)
      # okay here is where i think we need to start grouping by machine tags.
      if flickrMTNS:
        # i guess the first thing to do is loop through the tags and see if there's a NS 
        # /predicate match
        for machineTag in photosInfo[thisPhootID]['mTags']:
          if flickrMTNS in machineTag and flickrMTP in machineTag:
            # if there is a match, download it and split the string by `=` and get the value.
            # download the photo
            print picinfoList[-1].downloadPhoto()
            # update our master var!
            photosInfo[thisPhootID] = vars(picinfoList[-1])
            # okay, now store this phoot's ID in a list in a dict that's associated with this 
            # flickrMTV
            splitted = machineTag.split('=')
            flickrMTV = splitted[1]
            if flickrMTV in mTagGroups:
              mTagGroups[flickrMTV].append(thisPhootID)
            else:
              mTagGroups[flickrMTV] = []
              mTagGroups[flickrMTV].append(thisPhootID)
            # and break here? potential control flow problems here
            break
      else:
        # if there was no machine tag specified, download the file.
        # download the photo
        picinfoList[-1].downloadPhoto()
        # update our master var!
        photosInfo[thisPhootID] = vars(picinfoList[-1])
      # now let's store the data for intermediate results
      allPhotoInfo = {'photosInfoDict': photosInfo,'sortedDates':dateList,'dateTranslator':dateTranslator,'mTagGroupsDict':mTagGroups}
      with open(infoFname,'w') as outfile:
        json.dump(allPhotoInfo,outfile)
  
  # but get a flickr ID for all the phoots in the set or group.
  for record in outPhots:
    idList.append(record['id'])
    
  # now to determine if we need to trim the list. this should happen in two ways:
  # 1. a photo can "age out"---if there are more than the maximum number of photos specified,
  # and it's older than the last one in the list, it should be removed. UNLESS photo 
  # accretion is desired...
  # 2. if a photo is within valid age/list size limits and the image has been removed
  # from the flickr set.
  
  # here we gather data about the files that are already in our system.
  dateNameDict = {}
  idNameDict = {}
  
  for phootID in photosInfo:
    dateNameDict[photosInfo[phootID]['date']] = {'flickrID': phootID, 'imageFname': photosInfo[phootID]['filename']}
    idNameDict[phootID] = {'markedForDeletion': True, 'imageFname': photosInfo[phootID]['filename'], 'flickrID': phootID,}
  
  # NOW. Remove any IDs we find in `photosInfo` that aren't in `idList`.
  # first, check the list from the server against the list on our file system
  for id in idList:
    if id in idNameDict:
      idNameDict[id]['markedForDeletion'] = False;
  # then go through the list we just updated and delete any still marked for deletion.
  for dictItem in idNameDict:
    if idNameDict[dictItem]['markedForDeletion']:
      del photosInfo[idNameDict[dictItem]['flickrID']]
      # and remove the image too! otherwise weird things happen when you switch sets around
      remove(idNameDict[dictItem]['imageFname'])
  
  # FINALLY. Remove any photos that have aged out.
  if searchopts['autoCull'] == 'true':
    # if we actually need to cull anything, let's get a list of keys from the sorted dict.
    if len(dateList) > int(searchopts['numPhotos']):
      for delIndex in range(int(searchopts['numPhotos']) + 1,len(dateList) + 1):
        del photosInfo[dateNameDict[str(dateList[-delIndex])]['flickrID']]
        # and remove the image too! otherwise weird things happen when you switch sets around
        remove(dateNameDict[str(dateList[-delIndex])]['imageFname'])
  
  # get information about upload dates with respect to flickr IDs
  dateList, dateTranslator = wrangleDates(photosInfo, dateList, dateTranslator, True)
  
  # now let's store the data for future use
  allPhotoInfo = {'photosInfoDict': photosInfo,'sortedDates':dateList,'dateTranslator':dateTranslator,'mTagGroupsDict':mTagGroups}
  with open(infoFname,'w') as outfile:
    json.dump(allPhotoInfo,outfile)
