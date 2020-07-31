# GalleryGAE
An Google App Engine Gallery Project, where an individual user can have their own galleries, and in each gallery they can have many images.

This application uses basic authentication provided by google's "Users"  webapp2 package, where each user has their own sets of galleries and images. 

Three seperate classes are created for storing data

1) Customer - To store user id object and it's own galllery data
2) Gallery - To store images data
3) Image - To store an image by google's Blob Store key.

Along with the above I have added few other functionlities like, 
1) Restrict same name for multiple gallery
2) Detect same image 
3) The first uploaded image will be shown on gallery tile.
4) Galleries and Images page will be displayed in a Grid view.
5) User can Delete or Rename a gallery.
6) Delete an image.

To run this application,
1) Either you can download the google app engine desktop application
2) Can install google cloud sdk and deploy in local using command ./devappserver
3) Or Deploy to cloud and test.

This application is to test the basics of Google App Engine.
