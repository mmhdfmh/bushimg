import sys
import re
from PIL import Image
import numpy as np

def extract(src):
    bush = np.array(Image.open(src)).reshape(-1)
    it = iter(bush)
    
    name = []
    while True:
        name.append(0)
        for i in range(8):
            byte = next(it)
            name[-1] = (name[-1] << 1) | (byte & 1)
        if name[-1] == 0:
            break
    name = bytes(name[:-1]).decode('utf-8')
    
    output = re.sub(r'^(.*)\.(.+)$', r'\1_ext.\2', name)
    with open(output, 'wb') as ext:
        while True:
            char = 0
            for i in range(8):
                byte = next(it)
                char = (char << 1) | (byte & 1)
            if char == 0:
                break
            ext.write(bytes([char]))

def insertion(cover, embed):
    cf = np.array(Image.open(cover))
    img_shape = cf.shape
    cf = cf.reshape(-1)
    it = iter(range(len(cf)))
    ef = open(embed, 'rb')
    
    for byte in bytes(embed + '\0', 'utf-8'):
        for bit in range(7, -1, -1):
            try: idx = next(it)
            except StopIteration: raise RuntimeError('Image size is too small')
            cf[idx] = (cf[idx] & 254) | (byte >> bit & 1)
    
    while byte := ef.read(1):
        byte = byte[0]
        for bit in range(7, -1, -1):
            try: idx = next(it)
            except StopIteration: raise RuntimeError('Image size is too small')
            cf[idx] = (cf[idx] & 254) | (byte >> bit & 1)
    ef.close()
            
    for bit in range(7, -1, -1):
        try: idx = next(it)
        except StopIteration: raise RuntimeError('Image size is too small')
        cf[idx] = cf[idx] & 254

    output = re.sub(r'^(.*)\.(.+)$', r'\1_bush.\2', cover)
    Image.fromarray(cf.reshape(img_shape)).save(output)

if __name__ == '__main__':
    argv = sys.argv[1:]
    # cover, embed | src
    
    match len(argv):
        case 1: 
            extract(*argv)
            print('extract success')
        case 2: 
            insertion(*argv)
            print('insertion success')
        case _: raise RuntimeError('Arguments must be one or two')