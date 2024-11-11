from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import sys
import os
client = ImgurClient('dbcd9a0baa0e998', '23a02f2b6c7bd631096d7549af8c52f34b8ea654')
try:
    f= open("{0}.txt".format(sys.argv[2]),"w+")
    for image in client.get_album_images(sys.argv[1]):
        f.write("<img src=\""+image.link+"\" alt=\""+sys.argv[2]+"\">"+'\n')
        f.write(">"+'\n'+'\n')
    f.close()
except ImgurClientError as e:
    print('ERROR: {}'.format(e.error_message))
    print('Status code {}'.format(e.status_code))