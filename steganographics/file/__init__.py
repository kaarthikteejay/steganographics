import math

__version__ = '0.1'

def file_to_bin(path):
    #37 bits for exif: 5 for char length, 32 length of hidden data
    l = []
    bin_dat = ''
    with open(path, 'rb') as f:
        byte = f.read(1)
        while byte != b'':
            l.append(ord(byte))
            byte = f.read(1)
    bin_len = math.ceil(math.log(max(l), 2))
    for el in l:
        bin_dat += bin(el)[2:].zfill(bin_len)
    return bin(bin_len)[2:].zfill(5)+bin(len(bin_dat))[2:].zfill(32)+bin_dat
        
    

def bin_to_file(binary, path):
    bin_len = int(binary[:5],base=2)
    size = int(binary[5:37],base=2)
    binary = binary[37:]
    d = ''.join([chr(int(binary[i:i+bin_len],base=2)) for i in range(0,len(binary),bin_len)])
    f = open(path,'w')
    f.write(d)
    f.close()
    return True
