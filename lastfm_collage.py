# Forked by dudenugget2000

import random
from PIL import Image, ImageDraw
import requests
import sys
import urllib
import os
import glob

# api
try:
    my_file = open("api")
    my_file.close()
except IOError:
    key = input('Add your Last.fm API key: ')
    my_file = open("api", "w+")
    my_file.write(key)
    my_file.close()

my_file = open("api")
key = my_file.readline()
my_file.close()

# initializes cols and rows
cols = 0
rows = 0

# Asks user to enter their lastfm username
usr = input('Enter your Last.FM username: ')

# Asks user if they want to create a collage of artists or albums
print('1) Artists')
print('2) Albums')
ar_al = input('Would you like a collage of your artists or albums (1-2): ')
meth = ''
if ar_al == '1':
    meth = 'user.gettopartists'
elif ar_al == '2':
    meth = 'user.gettopalbums'
else:
    print('Invalid input, defaulting to artists')
    meth = 'user.gettopartists'

art = 'user.gettopartists'
alb = 'user.gettopalbums'

# Asks user to enter a time period of scrobbles
print('1) 1 Week')
print('2) 1 Month')
print('3) 3 Months')
print('4) 6 Months')
print('5) 12 Months')
print('6) Lifetime')
time_period = input('Enter the scrobble time period to illustrate (1-6): ')

str_time = ''
if time_period == '1':
    str_time = '7day'
elif time_period == '2':
    str_time = '6month'
elif time_period == '3':
    str_time = '3month'
elif time_period == '4':
    str_time = '6month'
elif time_period == '5':
    str_time = '12month'
elif time_period == '6':
    str_time = 'overall'
else:
    print('Invalid input, defaulting to 12 months')
    str_time = '12month'

print('1) 1x1')
print('2) 2x2')
print('3) 3x3')
print('4) 4x4')
print('5) 5x5')
print('6) 6x6')
sz = input('Enter a collage size (1-6): ')

if sz == '1':
    cols = 1
    rows = 1
elif sz == '2':
    cols = 2
    rows = 2
elif sz == '3':
    cols = 3
    rows = 3
elif sz == '4':
    cols = 4
    rows = 4
elif sz == '5':
    cols = 5
    rows = 5
elif sz == '6':
    cols = 6
    rows = 6
else:
    print('Invalid input, defaulting to 3x3')
    cols = 3
    rows = 3

# url --> LastFM API
url = "http://ws.audioscrobbler.com/2.0/"
# dictionary that holds the method used with the LastFM api, the user's LastFM
# username, the dev's api_key, the limit of artists/albums to fetch, the
# scrobble period to use when finding the user's top artists/albums, and the
# format of the api's output
body = {
    # for artists
    # 'method': "user.gettopartists",
    # for albums
    # 'method': "user.gettopalbums",
    'method': meth,
    'user': usr,
    'api_key': key, # <-- Last.fm Api Key Here
    'limit': (cols*rows),
    'period': str_time,
    'format': 'json'
}


# recieve response from LastFM API given the values in body
r = requests.get(url, body)

# if there is an error accessing the api then the program prints
# 'cannot access' and quits
if r.status_code == 403:
    print('cannot access')
    sys.exit()

# narrows down JSON to artists/albums based on previous user input
try:
    if meth == art:
        art_alb = r.json()['topartists']['artist']
    elif meth == alb:
        art_alb = r.json()['topalbums']['album']
# if there is no ['topartists/topalbums']['artist/album'] then the program
# exits stating that the username is invalid
except KeyError:
    print('Username does not exist')
    sys.exit()


def download_file(url, directory):
    # names downloaded images to be included in collage as newfile+ and a
    # random number between 1 and 1000
    no = random.randint(1, 1000)
    path = directory + "/" + 'newfile+{no}.jpg'.format(no=no)
    # dowloads individual photos to put into collage
    urllib.request.urlretrieve(url, path)  # <-- This works now!
    return path


# stores information about the name and location of each artist/album
image_info = []
for x in art_alb:
    # gets the link to the 300x300 image of the artist/album located in the
    # JSON
    url = x['image'][3]['#text']
    # calls the download_file function which downloads the individual images
    # to the current ('.') directory where the python file is located
    path = download_file(url, '.')
    # spot_info stores both the name of the artist/album and the file location
    # to the image of the artist/album
    spot_info = {
        'name': x['name'],
        'path': path,
    }
    # spot_info is appended to the list image_info
    image_info.append(spot_info)


# insert_name recieves the collage image ('image'), name of an
# individual image in the collage ('name'), and location on
# the collage to insert the name of the image
def insert_name(image, name, cursor):
    draw = ImageDraw.Draw(image, 'RGBA')
    x = cursor[0]
    y = cursor[1]
    draw.rectangle([(x, y+200), (x+300, y+240)], (0, 0, 0, 123))
    draw.text((x+8, y+210), name, (255, 255, 255))


# create_collage creates an empty image on which the collage is to be created
# and appends the previously downloaded individual artist/album pictures and
# pastes them onto the collage canvas
#
# cells --> list with dictionaries holding the name and path of
# each artist/album (in this case it is image_info
# cols --> columns, default 3
# rows --> rows, default 3
def create_collage(cells, cols=3, rows=3):
    # w --> image width (in this case 300)
    # h --> image height (in this case 300)
    w, h = Image.open(image_info[0]['path']).size
    # stores width of collage image (blank canvas on which the images will be
    # pasted)
    collage_width = cols * w
    # stores height of collage image
    collage_height = rows * h
    # creates blank collage image
    new_image = Image.new('RGB', (collage_width, collage_height))
    # cursor starts at the origin
    cursor = (0, 0)
    for cell in cells:
        # place image
        new_image.paste(Image.open(cell['path']), cursor)

        # add name
        insert_name(new_image, cell['name'], cursor)

        # move cursor
        y = cursor[1]
        x = cursor[0] + w
        if cursor[0] >= (collage_width - w):
            y = cursor[1] + h
            x = 0
        cursor = (x, y)
    # saves collage as collage.png
    new_image.save('collage.png', 'png')
    # displays image
    new_image.show()
    # removes all assets used to make collage
    for file in glob.glob("./newfile+*"):
        os.remove(file)


create_collage(image_info, cols, rows)
# create_collage(image_info, cols=4, rows=4)
