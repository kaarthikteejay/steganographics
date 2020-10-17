from PIL import Image
import itertools

from exceptions import *


MODES = ('RGB', 'HSV', 'RGBA', 'CMYK') #Supported modes
MODES_3 = ('RGB', 'HSV') #Supported modes with three bands
MODES_4 = ('RGBA', 'CMYK') #Supported modes with four bands

class SteganoImage:
    def __init__(self, path, name):
        self.path = path
        self.name = name
        self.img = Image.open(path)
        self.color_mode = self.img.mode
        self.num_bands = len(self.img.getbands())
        self.color_range = range(256) #Maximum values for most image modes
        if self.color_mode not in MODES:
            UnsupportedMode(self.color_mode).warn()
    def __repr__(self):
        return '{}(path={},mode={})'.format(self.name,self.path,self.color_mode)
def image_to_bin(path):
    #Write most important Exif: Color mode and size
    modes = {'RGB':'00', 'HSV' : '01', 'RGBA' : '10', 'CMYK' : '11'}
    output = ''
    img = Image.open(path)
    try:
        mode = modes[img.mode]
    except KeyError:
        if len(img.getbands()) not in (3,4):
            raise UnsupportedMode(img.mode)
        if len(img.getbands()) == 3:
            mode = 'RGB'
        else:
            mode = 'RGBA'
    width,height = img.size
    width = bin(width)[2:].zfill(16)
    height = bin(height)[2:].zfill(16)
    exif = mode+width+height
    px = [list(img.getpixel((x,y))) for x in range(img.width) for y in range(img.height)]
    for p in px:
        for e in p:
            output += bin(e)[2:].zfill(8)
    return exif+output

def bin_to_image(binary, save_path, char_length=8):
    #Read most important Exif: Color mode and size
    modes = {'00':'RGB', '01' : 'HSV', '10' : 'RGBA', '11' : 'CMYK'}
    #First two bits are for color mode
    #Next 32 bits are for width and height. 16 each, which gives a maximum height/width of 65536
    exif = binary[:34]
    binary = binary[34:]
    d = [binary[i:i+char_length] for i in range(0,len(binary),char_length)]
    mode = modes[exif[:2]]
    bands = 3
    if mode in ('RGBA', 'CMYK'):
        bands = 4
    width = int(exif[2:18],2)
    height = int(exif[18:],2)
    d = [int(i,2) for i in d]
    args = [iter(d)]*bands
    px =  list([e for e in t if e != None] for t in itertools.zip_longest(*args)) 
    pic = Image.new(mode,(width,height))
    i = 0
    for x in range(pic.width):
        for y in range(pic.height):
            try:
                t = tuple(px[x*pic.height+y])
                pic.putpixel((x,y),t)
            except IndexError:
                i += 1
    pic.save(save_path)
    pic.close()
