#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import json
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.ext.ndb import Key
from google.appengine.ext.webapp import blobstore_handlers


import webapp2


def readFile(filename):

    file = open("/Front-End/"+filename)
    file_text = file.read()
    file.close()
    return file_text

#Defining the model

class UserToCustomer(db.Model):

    customer_key = db.StringProperty()

def GetCustomer():

    user=getCurrentUser()
    userCustomer=UserToCustomer.get_by_key_name(user.user_id())

    return Customer.get_by_id(userCustomer.customer_key)


class Image(ndb.Model):

    imageName=ndb.StringProperty(indexed=False)
    blob_key=ndb.BlobKeyProperty()
    user_id=ndb.StringProperty(indexed=False)

class Gallery(ndb.Model):

    imageNames = ndb.StringProperty(indexed=False)
    galleryName = ndb.StringProperty(indexed=False)
    user_id=ndb.StringProperty(indexed=False)

class Customer(ndb.Model):

    galleryNames = ndb.StringProperty(indexed=False)
    user_id=ndb.StringProperty(indexed=False)

######Model definition ends

###Utility Functions
def split(name):

    return name.split('@')[0]

def getCurrentUser():

    return users.get_current_user()

def getDictionary(data):

    if data == '{}':

        data = {}
    else:

        data = json.loads(data)

    return data

def getString(data):

    return json.dumps(data)

def galleryPreProcess(data):

    deleteNames = []
    for name, link in data.items():

        gallery = Gallery.get_by_id(link)

        if gallery == None:

            del data[name]

    for i in deleteNames:

        del data[i]

    return data

def imagePreProcess(data):

    deleteNames = []
    for name in data:

        image = Image.get_by_id(data[name])

        if image == None:

            deleteNames.append(name)
        
    for i in deleteNames:
        
        del data[i]

    return data

def isDuplicate(name, data):

    data = getDictionary(data)

    if name in data:

        return True
    else:

        return False

def isNotCurrentUserData(id, types):

    user = getCurrentUser()

    if types == "Gallery":

        gallery = Gallery.get_by_id(id)

        #return gallery.user_id + " " + str(user.user_id())

        if gallery.user_id != str(user.user_id()):

            return True
        else:

            return False
        

    if types == "Image":

        image = Image.get_by_id(id)

        if image.user_id != user.user_id():

            return True
        else:

            return False

#imageName, galleryid
def isDuplicateImage(imageName):

    customer = GetCustomer()

    galleryData = getDictionary(customer.galleryNames)

    for name, value in galleryData.items():

        tempGallery = Gallery.get_by_id(name)

        tempImageData = getDictionary(tempGallery.imageNames)

        for image in tempImageData:

            if imageName == Image.get_by_id(image).imageName:

                return tempGallery.galleryName

    return None

###Utility Functions ENDS
#/galleries/
class GalleryPage(webapp2.RequestHandler):

    def get(self):

        user=getCurrentUser()

        if not user:

            self.redirect("/", abort=True)

        customer=GetCustomer()
        #self.response.out.write(customer)
        #customer.galleryNames = '{}'
        #customer.put()
        
        galleryData = getDictionary(customer.galleryNames)
        galleryData=galleryPreProcess(galleryData)

        customer.galleryNames = getString(galleryData)
        customer.put()
        
        if galleryData == {}:

            html = readFile("uploadgallery.html")
            url = users.create_logout_url('/')
            html += '<div style="text-align:center;"><a href='+'"'+url+'"'+'" class="btn btn-large primary" style="align-items: center;">Logout</a></div>'
            self.response.out.write(html)
        else:

            html = readFile("firsthalf.txt")
            #print html
            logouturl = users.create_logout_url("/")
            html+='<div class="col-lg-12"><h1 class="page-header">'+split(user.nickname())+' - Galleries'+'</h1><a href="'+logouturl+'" class="btn btn-primary">Logout</a> <a href="/galleryform/" class="btn btn-primary">New Gallery</a></div>'
        
            for name, link in galleryData.items():

                reference="/images/"+link
                gallery=Gallery.get_by_id(link)

                gallery.imageNames = getString(imagePreProcess(getDictionary(gallery.imageNames)))

                #self.response.out.write(gallery)
                
                if gallery.imageNames == '{}':

                    deleteReference="/deletegallery/"+str(link)
                    editReference="/editgallery/"+str(link)
                    html += '<div class="col-lg-3 col-md-4 col-xs-6 thumb"><a class="thumbnail" href='+'"'+reference+'"'+'><img class="img-responsive" border="0" height="300" src='+'"'+'images/1.jpg'+'"'+'width="400" /></a><a class="btn btn-primary" href='+'"'+deleteReference+'"'+'>Delete</a><a class="btn btn-primary" href='+'"'+editReference+'"'+'>Edit</a><p style="text-align: center; font-family:'+"Segoe UI"+', Tahoma, Geneva, Verdana, sans-serif">'+name+'</p></div>'
                else:

                    firstImageData=list(getDictionary(gallery.imageNames).keys())[0]

                    firstImage = Image.get_by_id(firstImageData)

                    imageReference="/view_photo/"+str(firstImage.blob_key)

                    deleteReference="/deletegallery/"+str(link)

                    editReference="/editgallery/"+str(link)

                    html += '<div class="col-lg-3 col-md-4 col-xs-6 thumb"><a class="thumbnail" href='+'"'+reference+'"'+'><img class="img-responsive" border="0" height="300" src='+'"'+imageReference+'"'+'width="400" /></a><a href="'+deleteReference+'" class="btndelete btn-primary">Delete</a><a class="btnedit btn-primary" href='+'"'+editReference+'"'+'>Edit</a><p style="text-align: center; font-family:'+"Segoe UI"+', Tahoma, Geneva, Verdana, sans-serif">'+name+'</p></div>'
                
            html += readFile("secondhalf.txt")

            self.response.out.write(html)

        
        
        
#/editgallery/<gid>
class EditGallery(webapp2.RequestHandler):


    def get(self, galleryid):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if isNotCurrentUserData(galleryid, "Gallery"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)
        else:

            html = readFile("galleryeditform.html")

            self.response.out.write(html.format(galleryid))

    def post(self, galleryid):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if isNotCurrentUserData(galleryid, "Gallery"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)
        else:

            galleryName = self.request.get("galleryname")
            
            customer = GetCustomer()

            gallery = Gallery.get_by_id(galleryid)

            galleryData = getDictionary(customer.galleryNames)

            #self.response.out.write(newGalleryName)
            
            if galleryName == gallery.galleryName or isDuplicate(galleryName, customer.galleryNames):

                html = readFile("editerrorgallery.html")
                #self.response.out.write("In Same")
                self.response.out.write(html.format(galleryName))
            
            else:

                newGallery = Gallery(id=galleryName,
                    imageNames = gallery.imageNames,
                    galleryName = galleryName,
                    user_id = gallery.user_id)

                newGallery.put()

                gallery.key.delete()

                galleryData[galleryName] = newGallery.key.id()

                galleryData = getString(galleryData)

                customer.galleryNames=galleryData

                customer.put()

                self.redirect("/galleries/")
        


#/images/<galleryId>
class ImagePage(webapp2.RequestHandler):
    
    def get(self, galleryid):

        if not getCurrentUser():

            self.redirect("/", abort=True)


        if isNotCurrentUserData(galleryid, "Gallery"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)

        else:
            gallery = Gallery.get_by_id(galleryid)

            #self.response.out.write(gallery.key.id())
            imageData = getDictionary(gallery.imageNames)
            #self.response.out.write(imageData)
            
            imageData = imagePreProcess(imageData)

            gallery.imageNames = getString(imageData)

            gallery.put()
            
            if imageData == {}:

                html = readFile("uploadimage.html")
                
                self.response.out.write(html.format(gallery.key.id()))
            else:

                html = readFile("firsthalf.txt")
                logouturl = users.create_logout_url("/")
                html+='<div class="col-lg-12"><h1 class="page-header">'+galleryid+' -Images'+'</h1><a href="'+logouturl+'" class="btn btn-primary">Logout</a> <a href="/imageform/'+gallery.key.id()+'" class="btn btn-primary">Upload Image</a> <a href="/galleries/" class="btn btn-primary">Back To Gallery</a></div>'
                
                for name in imageData:

                    image = Image.get_by_id(imageData[name])
                    reference="/view_photo/"+str(image.blob_key)

                    deletereference="/deleteimage/"+imageData[name]

                    html += '<div class="col-lg-3 col-md-4 col-xs-6 thumb"><a class="thumbnail" href='+'"'+reference+'"'+'><img class="img-responsive" border="0" height="300" src='+'"'+reference+'"'+'width="400" /></a><a href="'+deletereference+'" class="btn btn-primary">Delete</a><p style="text-align: center; font-family:'+"Segoe UI"+', Tahoma, Geneva, Verdana, sans-serif">'+name+'</p></div>'
                
                html += readFile("secondhalf.txt")


                self.response.out.write(html)
        
            
        
#/galleryform/
#-Completed
class NewGalleryFormHandler(webapp2.RequestHandler):

    def get(self):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        html = readFile("galleryformhtml.html")

        self.response.out.write(html)
    
    def post(self):

        if not getCurrentUser():

            self.redirect("/")

        galleryName = self.request.get("galleryname")

        print "Gallery name given is "+ galleryName
        #self.response.out.write(galleryName)
        
        customer = GetCustomer()

        galleryData = customer.galleryNames

        if isDuplicate(galleryName, galleryData):

            html = readFile("duplicateGallery.html")

            self.response.out.write(html.format(galleryName))
        else:
            gallery = Gallery(
                id=galleryName,
                imageNames = '{}',
                galleryName=galleryName,
                user_id=customer.key.id())
            
            gallery.put()

            #self.response.out.write(Gallery.get_by_id(galleryName))
            
            tempGalleryNames=getDictionary(customer.galleryNames)
            tempGalleryNames[galleryName] = galleryName
            tempGalleryNames = getString(tempGalleryNames)

            customer.galleryNames = tempGalleryNames

            customer.put()
            
            self.redirect("/galleries/")
        
        

#/imageform/<gid>
class NewImageFormHandler(webapp2.RequestHandler):

    def get(self, galleryid):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if isNotCurrentUserData(galleryid, "Gallery"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)
        else:
        
            upload_url = blobstore.create_upload_url('/upload_photo/'+galleryid)
            html = readFile("imageform.html")

            self.response.out.write(html.format(upload_url, galleryid))

        
#/upload_photo/<gid>
class PhotoUploadHandler(blobstore_handlers.BlobstoreUploadHandler):

    def post(self, galleryid):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if isNotCurrentUserData(galleryid, "Gallery"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)

        else:

            imageName = self.request.get("imageName")

            isDuplicate = isDuplicateImage(imageName)

            if isDuplicate != None:

                html = readFile("duplicateimage.html")
                self.response.out.write(html.format(str(isDuplicate)))

            else:

                gallery = Gallery.get_by_id(galleryid)

                #self.response.out.write(self.get_uploads()[0].filename)

                upload = self.get_uploads()[0]
                imageFile = upload.filename
                extension = (os.path.splitext(imageFile)[1]).lower()
                #self.response.out.write(extension)
                if extension == ".jpg" or extension == ".png":

                    image = Image(
                        id=imageName,
                        blob_key=upload.key(),
                        imageName=imageName,
                        user_id=GetCustomer().key.id())

                    image.put()

                    imageNames = getDictionary(gallery.imageNames)
                    imageNames[imageName] = image.key.id()
                    imageNames = getString(imageNames)

                    gallery.imageNames=imageNames

                    gallery.put()
                    self.redirect('/galleries/')
                else:

                    html = readFile("invalidExtension.html")

                    self.response.out.write(html)

#     
class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)


#/deletegallery/<gid>
#checks if any images are there in gallery and deletes if no images are there
class DeleteGallery(webapp2.RequestHandler):

    def get(self, galleryid):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if isNotCurrentUserData(galleryid, "Gallery"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)
        else:

            gallery = Gallery.get_by_id(galleryid)

            if gallery.imageNames == '{}':

                gallery.key.delete()
                self.redirect("/galleries/")
            else:

                html = readFile("galleryalert.html")
                self.response.out.write(html)


#/deleteimage/<imageid>
class DeleteImage(webapp2.RequestHandler):

    def get(self, imageid):

        if not getCurrentUser():

            self.redirect("/", abort=True)

        if isNotCurrentUserData(imageid, "Image"):

            html = readFile("invalidUser.html")
            self.response.out.write(html)
        else:

            image = Image.get_by_id(imageid)

            image.key.delete()

            self.redirect("/galleries/")

#/
class MainPage(webapp2.RequestHandler):

    def get(self):

        user = users.get_current_user()
        print "Before Redirect"
  
        if user:
            #Creating an UserTo Customer using user_id
            userCustomer=UserToCustomer.get_by_key_name(user.user_id())
            
            if userCustomer == None:

                userCustomer = UserToCustomer(key_name=user.user_id())
                userCustomer.customer_key=""
                userCustomer.put()

            if userCustomer.customer_key == "":

                newCustomer=Customer(id=user.user_id(), galleryNames='{}')
            
                newCustomer.put()

                userCustomer.customer_key=str(newCustomer.key.id())

                db.put(userCustomer)

            self.redirect('/galleries/')
            
        else:

            url = users.create_login_url(self.request.uri)
            html = readFile("Login.html")
            self.response.write(html.format(url))
        

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/galleries/', GalleryPage),
    ('/galleryform/', NewGalleryFormHandler),
    ('/images/([^/]+)?', ImagePage),
    ('/imageform/([^/]+)?', NewImageFormHandler),
    ('/upload_photo/([^/]+)?', PhotoUploadHandler),
    ('/view_photo/([^/]+)?', ViewPhotoHandler),
    ('/deletegallery/([^/]+)?', DeleteGallery),
    ('/deleteimage/([^/]+)?', DeleteImage),
    ('/editgallery/([^/]+)?', EditGallery)
], debug=True)


