'''
Code is sourced from codegolf stackexchange. 
https://codegolf.stackexchange.com/questions/33172/american-gothic-in-the-palette-of-mona-lisa-rearrange-the-pixels
Attributed to user Calvin's Hobbies.
https://codegolf.stackexchange.com/users/26997/calvins-hobbies
'''

from __future__ import division,print_function
import os
import sys
from PIL import Image
import numpy as np

def print_replace(line):
  ERASE_LINE = '\x1b[2K\r'
  print(ERASE_LINE,end='')
  print(line,end='')
  sys.stdout.flush()
 
#returns dict of (color -> pixel list) pairs
def imgColorLocs(img):
    data = img.load()
    colorLocs = {}
    for x in range(img.size[0]):
        for y in range(img.size[1]):
            color = data[x, y]
            if color in colorLocs:
                colorLocs[color].append((x, y))
            else:
                colorLocs[color] = [(x, y)]
    return colorLocs
 
#returns a tuple of 3 ordered pairs: the canvas size, the src position, and the dst position
def getCanvasDims(src, dst, in_place):
    w = max(src.size[0], dst.size[0])
    h = max(src.size[1], dst.size[1])
    offset = lambda dim, canvasDim: int(0.5 * (canvasDim - dim))
    srcPos = offset(src.size[0], w), offset(src.size[1], h)
    dstPos = offset(dst.size[0], w), offset(dst.size[1], h)
    if not in_place:
        dstPos = dstPos[0] + w, dstPos[1]
        w *= 2
    return (w, h), srcPos, dstPos
 
def dist(loc1, loc2):
    return ((loc2[0] - loc1[0])**2 + (loc2[1] - loc1[1])**2)**0.5
 
#returns list of tuples of the closest color ((srcx, srcy), (dstx, dsty), (r, g, b))
def getMappings(src, srcOffset, dst, dstOffset):
    add = lambda t1, t2: (t1[0] + t2[0], t1[1] + t2[1])
    srcColorLocs = imgColorLocs(src)
    dstColorLocs = imgColorLocs(dst)
    mappings = []
    for color in srcColorLocs:
        srcLocs = srcColorLocs[color]
        dstLocs = dstColorLocs[color]
        for srcLoc in srcLocs:
            minDist = dist((0, 0), src.size)
            index = 0
            for i, dstLoc in enumerate(dstLocs):
                d = dist(srcLoc, dstLoc)
                if d < minDist:
                    minDist = d
                    index = i
            dstLoc = dstLocs.pop(index)
            mappings.append((add(srcLoc, srcOffset), add(dstLoc, dstOffset), color))
    return mappings
 
def makeLinearMapper(n_frames):
    def linearMapper(startLoc, stopLoc, step):
        m = lambda start, stop: (stop - start) * step / n_frames + start
        return (m(startLoc[0], stopLoc[0]), m(startLoc[1], stopLoc[1]))
    return linearMapper
 
#src is the filename of the palette image that will be rearranged
#dst if the filename of the final rearranged palette
#n_frames is the number of increments between src and dst, n_frames + 1 images are generated in total
#folder is the location all intermediate images will save to
#background is the background of the intermediate images
#when cycle is true a duplicate set of images will be made with higher numbers in reverse order, useful for making continuous looking gifs
#when in_place is true the transforming images are drawn on top of one another
#when draw_src is true the src image is drawn below the moving pixels
#when draw_dst is true the dst image is drawn below the moving pixels
def animate(src,dst,verbose=True,background='black',cycle=False,in_place=True, \
      draw_src=False,draw_dst=False,n_frames=30,fps=30,start_duration=1, \
      end_duration=1):
    if verbose:
        print('Animating frames...')
  
    cycle_factor = 0.5 if cycle else 1 #hacky way of making start/end duration half as long and then reversing
 
    src = Image.fromarray(src).convert('RGB')
    dst = Image.fromarray(dst).convert('RGB')
    if sorted(src.getdata()) != sorted(dst.getdata()):
        raise ValueError('Source and destination images don\'t have the same pixels.')
 
    canvasDims = getCanvasDims(src, dst, in_place)
    mappings = getMappings(src, canvasDims[1], dst, canvasDims[2])
    mapper = makeLinearMapper(n_frames)
  
    all_imgs = []
    frame_list = [0]*int(start_duration*fps*cycle_factor)
    frame_list.extend(range(1,n_frames))
    frame_list.extend([n_frames]*int(end_duration*fps*cycle_factor))
    for ind,step in enumerate(frame_list):
        if verbose:
            print_replace('Generating image %d of %d\r' % (ind + 1, len(frame_list)))
 
        img = Image.new('RGB', canvasDims[0], background)
        if draw_src:
            img.paste(src, canvasDims[1])
        if draw_dst:
            img.paste(dst, canvasDims[2])
        data = img.load()
        for startLoc, stopLoc, color in mappings:
            x, y = mapper(startLoc, stopLoc, step)
            data[x, y] = color
        all_imgs.append(np.array(img))
    if verbose:
        print()
    
    if cycle:
        all_imgs.extend(reversed(all_imgs))
      
    return all_imgs