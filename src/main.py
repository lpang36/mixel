from __future__ import division,print_function
from PIL import Image
import numpy as np
import imageio
from animate import animate as generate_frames
from anneal import anneal
from pixel_sort import pixel_sort
import cProfile
from functools import reduce
import time

def adaptive_resize(cur_width,cur_height,target_size):
	if cur_width*cur_height==target_size:
		return cur_width,cur_height
	factors = set()
	for i in range(1,int(target_size**0.5)+1):
		if target_size%i==0:
			factors.add(i)
			factors.add(target_size//i)
	best_ratio = float('inf')
	best_output = (cur_width,cur_height)
	for i in factors:
		j = target_size//i
		candidate_ratio = (j/i)/(cur_height/cur_width)
		if candidate_ratio<1:
			candidate_ratio = 1/candidate_ratio
		if candidate_ratio<best_ratio:
			best_ratio = candidate_ratio
			best_output = i,j
	return best_output

def mix(input_path,target_path,output_path,algorithm='sort',animate=False, \
		anneal_options=None,animate_options=None,verbose=True):
	if animate_options is None:
		animate_options = {}
	for option in animate_options:
		if option in ['fps','n_frames','start_duration','end_duration']:
			if animate_options[option]<=0:
				raise ValueError('%s must be positive' % option)
	if 'n_frames' in animate_options and animate_options['n_frames']<0:
		raise ValueError('n_frames must be non-negative')
	if anneal_options is None:
		anneal_options = {}
	if 'n_steps' in anneal_options and 'stop_limit' in anneal_options:
		raise ValueError('At most one of n_steps and stop_limit can be specified.')
		
	input_img = Image.open(input_path).convert(mode='RGB')
	target_img = Image.open(target_path).convert(mode='RGB')
	
	new_input_dims = adaptive_resize(input_img.size[0],input_img.size[1], \
					 target_img.size[0]*target_img.size[1])
	input_img = input_img.resize(new_input_dims)
	
	input_img = np.array(input_img)
	target_img = np.array(target_img)
	
	base_input_img = np.copy(input_img)
	input_img = np.reshape(input_img,target_img.shape)
	
	start_time = time.time()
	if algorithm.lower()=='sort':
		output_img = pixel_sort(input_img,target_img)
		if verbose:
			print('Elapsed time: %.2fs' % (time.time()-start_time))
			start_time = time.time()
	elif algorithm.lower()=='anneal':
		output_img = anneal(input_img,target_img,verbose,**anneal_options)
		if verbose:
			print('Elapsed time: %.2fs' % (time.time()-start_time))
			start_time = time.time()
	elif algorithm.lower()=='hybrid':
		sorted_img = pixel_sort(input_img,target_img,verbose)
		if verbose:
			print('Elapsed time: %.2fs' % (time.time()-start_time))
			start_time = time.time()
		output_img = anneal(sorted_img,target_img,verbose,**anneal_options)
		if verbose:
			print('Elapsed time: %.2fs' % (time.time()-start_time))
			start_time = time.time()
	else:
		raise ValueError('Invalid algorithm type: %s' % algorithm)
	
	if output_path.endswith('.gif') or animate:
		frames = generate_frames(base_input_img,output_img,verbose,**animate_options)
		if verbose:
			print('Elapsed time: %.2fs' % (time.time()-start_time))
			print('Saving frames to %s' % output_path)
		imageio.mimsave(output_path,frames,duration=1/animate_options['fps'] \
						if 'fps' in animate_options else 1/30)
	else:
		if verbose:
			print('Saving image to %s' % output_path)
		Image.fromarray(output_img).save(output_path)
		
if __name__=='__main__':
	mix('../test/images/starry_night.png','../test/images/mona_lisa.png','../test/output/sn2ml_cycle.gif',algorithm='sort',animate_options={'cycle':True},anneal_options={'n_steps':1000000})