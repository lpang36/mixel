from __future__ import division,print_function
from PIL import Image
import numpy as np
import imageio
from animate import animate as generate_frames
#from anneal import anneal
from pixel_sort import pixel_sort
import cProfile

def mix(input_path,target_path,output_path,algorithm='sort',animate=False, \
		anneal_options=None,animate_options=None):
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
	
	input_img = input_img.resize(target_img.size)
	
	input_img = np.array(input_img)
	target_img = np.array(target_img)
	
	if algorithm.lower()=='sort':
		output_img = pixel_sort(input_img,target_img)
	elif algorithm.lower()=='anneal':
		#output_img = anneal(input_img,target_img,**anneal_options)
		pass
	elif algorithm.lower()=='hybrid':
		#sorted_img = pixel_sort(input_img,target_img)
		#output_img = anneal(sorted_img,target_img,**anneal_options)
		pass
	else:
		raise ValueError('Invalid algorithm type: %s' % algorithm)
	
	if output_path.endswith('.gif') or animate:
		frames = generate_frames(input_img,output_img,**animate_options)
		imageio.mimsave(output_path,frames,duration=1/animate_options['fps'] \
						if 'fps' in animate_options else 1/30)
	else:
		Image.fromarray(output_img).save(output_path)
		
if __name__=='__main__':
	mix('../test/images/starry_night.png','../test/images/mona_lisa.png','../test/output/test.gif',animate=True,animate_options={'cycle':True})