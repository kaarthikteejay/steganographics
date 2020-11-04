from PIL import Image
import itertools
import warnings

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
    if i>0:
        warnings.warn("Something went wrong. Maybe you weren't using image_to_bin to convert the original image to bin. {} pixel haven't been put to the image.".format(i))

class LSB(SteganoImage):
    def __init__(self, path):
        super().__init__(path,'LSB')
    def _bin_add(self,number,binary,bin_per_p=1):
        """Change the last x binary digits of a number"""
        n = bin(number)
        n = n[:-len(binary)]+binary
        d =  int(n,2)
        if d > max(self.color_range):
            d -= 2**bin_per_p
        elif d < min(self.color_range):
            d += 2**bin_per_p
        return d
    def _multiple_add(self, px, b, bin_per_p=1):
        pixel = list(px)
        binary = b
        bin_split = [binary[i:i+bin_per_p] for i in range(0,len(binary),bin_per_p)]
        i = 0
        for p,b in zip(pixel,bin_split):
            pixel[i] = self._bin_add(p,b,bin_per_p)
            i += 1
        return tuple(pixel)
    def read(self,amount=1,bin_per_p=1, scattering=(1,1), reverse=False): #Read only amount%, use less than 1 for small amounts data
        output = ''
        scattering = list(scattering)
        for x in range(0,int(self.img.width*amount),scattering[0]):
            for y in range(0,self.img.height,scattering[1]):
                p = list(self.img.getpixel((x,y)))
                for e in p:
                    output += bin(e)[-bin_per_p:]
        return output
    def max_hide(self,bin_per_p=1,scattering=(1,1)):
        """Return maximum bits that can be hidden"""
        scattering = list(scattering)
        return self.img.width*self.img.height*3*bin_per_p/scattering[0]/scattering[1]
    def hide(self, obj, path, bin_per_p=1, scattering=(1,1), reverse=False): #Input bin data and write to image
        """obj: binary data
           path: final path
           bin_per_p: bits per single pixel value that will be changed
           scattering: only hide data in every nth width/mth height   
           reverse: Start at the bottom right and go to top left
        """
        scattering = list(scattering)
        if os.path.splitext(self.path)[1][1:].lower() in ('jpg', 'jpeg'):
            CompressionWarning(self.name, os.path.splitext(self.path)[1]).warn()
        if bin_per_p >= 4:
            warnings.warn("bin_per_p should be 2 or 1, else the steganography can be discovered!")
        new_img = self.img.copy()
        bin_dat = [obj[i:i+self.num_bands*bin_per_p] for i in range(0,len(obj),self.num_bands*bin_per_p)] #'hello world' --> ['hel', 'lo ', 'wor', 'ld'] (but in binary)
        i = 0
        for x in range(0,self.img.width,scattering[0]):
            for y in range(0,self.img.height,scattering[1]):
                try:
                    new_img.putpixel((x,y),self._multiple_add(self.img.getpixel((x,y)),bin_dat[i],bin_per_p))
                    i += 1
                except IndexError:
                    break
            else:
                continue
            break
        else:
            warnings.warn("Not every bit could be written to the image!")
        new_img.save(path)
        return True
     
