#
#
#
#

import cv2 as cv
import numpy as np
from math import tanh

# arbitrary group of symbols selected ordered from darkest to lightest
SYMBOLS = ['`',"'",'^','.',',','*','_',';','+','!','\\','(',']','}','&','%','$','@', '#']

def closest_color(incolor):
  '''rounds an 8-bit color to one from 0 -> len(SYMBOLS)'''
  ivals    = len(SYMBOLS)
  incolor /= 255
  incolor *= ivals
  return int(incolor + 0.5)

def contrast(color):
  '''contrast glt curve'''
  color /= 255
  color  = (tanh(4*color - 2) + 1)/2
  return int(255*color)

def ascii_image(image, width):
  '''uses floyd steinberg dithering to find new pixel values'''

  # resize input image
  h, w    = image.shape
  ratio   = width/w
  image   = cv.resize(image, dsize=(width, int(h*ratio/1.7714285714)))
  h, w    = image.shape
  # create output array
  out     = np.zeros((h, w), dtype=np.uint8)
  ivals   = len(SYMBOLS)

  # add contrast to input
  for x in range(w):
    for y in range(h):
      image[y, x] = contrast(image[y, x])

  # main algorithm, round to closest new value using 
  # closest_color and propogate error to nearby pixels
  for x in range(w):
    for y in range(h):
      # find new value
      newval    = closest_color(image[y, x])
      out[y, x] = newval
      error     = image[y, x] - (255*newval/ivals)
      # propogate error
      if x < w-1:
        # pixel immediately to the left gets 7/16 of the error
        b4err  = image[y, x+1]
        b4err += error*7/16
        if b4err >= 0 and b4err < 256:
          image[y, x+1] = int(b4err)
      if x > 0 and y < h-1:
        # pixel below and to the left gets 3/16 of the error
        b4err  = image[y+1, x-1]
        b4err += error*3/16
        if b4err >= 0 and b4err < 256:
          image[y+1, x-1] = int(b4err)
      if y < h-1:
        # pixel below gets 5/16 of the error
        b4err  = image[y+1, x]
        b4err += error*5/16
        if b4err >= 0 and b4err < 256:
          image[y+1, x] = int(b4err)
      if x < h-1 and y < h-1:
        # diagonal pixel gets 1/16 of the error
        b4err  = image[y+1, x+1]
        b4err += error*1/16
        if b4err >= 0 and b4err < 256:
          image[y+1, x+1] = int(b4err)

  # write output to text file
  with open('out.txt', 'w')as fi:
    for y in range(h):
      for x in range(w):
        fi.write(SYMBOLS[out[y, x]-1])
      if y < h-1:
        fi.write('\n')

def main(argv) -> int:
  if len(argv) != 3:
    print('Usage: python3 ' + argv[0] + ' <input image path> <width in ascii chars>') 
    return 1
  image = cv.imread(argv[1])
  image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
  ascii_image(image, int(argv[2]))
  return 0

if __name__ == '__main__':
  import sys
  main(sys.argv)
