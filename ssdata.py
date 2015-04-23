#!/usr/bin/python

# Base URL part, no trailing slash
urlbase = 'https://spotseeker-test.cac.washington.edu'

# URL piece for a space
spaceurl = urlbase + '/seattle/cap:1/%(id)s'

# URL for favorites
faveurl = urlbase + '/favorites'

loginurl = urlbase + '/login'
logouturl = urlbase + '/logout?next=/'

shareurl = urlbase + '/share/%(id)s?back=%%2Fseattle%%2Fca%%3A1%%2F%(id)s'

exampleSpace = 4289
