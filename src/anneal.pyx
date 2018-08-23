from __future__ import division,print_function
import numpy as np
cimport numpy as np 
import colorsys
from random import randint,random
from math import exp

DTYPE = np.int
ctypedef np.int_t DTYPE_t

cpdef dist(pixel1,pixel2,r_weight,g_weight,b_weight):
	cdef float total = 0
	total+=abs(pixel1[0]-pixel2[0])*r_weight
	total+=abs(pixel1[1]-pixel2[1])*b_weight
	total+=abs(pixel1[2]-pixel2[2])*g_weight
	#for color1,color2,weight in zip(pixel1,pixel2,weights):
	#	total+=((color2-color1)**2)*weight
	return total
	
cpdef swap(array,x1,x2,y1,y2):
	array[y1,x1],array[y2,x2] = array[y2,x2],array[y1,x1]

def anneal(np.ndarray[DTYPE_t,ndim=3] input_img,np.ndarray[DTYPE_t,ndim=3] target_img, \
		   rgb_weights=(0.2126,0.7152,0.0722),init_rand=0,rand_decay=0, \
		   n_steps=None,stop_limit=None):
	if init_rand<0:
		raise ValueError('init_rand must be non-negative')
	if rand_decay<0:
		raise ValueError('rand_decay must be non-negative')
	if any([x<0 for x in rgb_weights]):
		raise ValueError('All rgb_weights must be non-negative')
	if n_steps is None and stop_limit is None:
		n_steps = 100000
		step_flag = True
	elif n_steps is not None:
		step_flag = True
	else:
		step_flag = False
		
	output_img = np.copy(input_img)
	
	cdef float r_weight,g_weight,b_weight
	r_weight,g_weight,b_weight = rgb_weights
	
	cdef int x1,x2,y1,y2,height,width
	cdef float current_dist,candidate_dist,flip_chance
		
	cdef int step_count = 0
	cdef int no_change_count = 0
	height,width,_ = output_img.shape
	while step_count<n_steps if step_flag else no_change_count>stop_limit:
		x1 = randint(0,width-1)
		x2 = randint(0,width-1)
		y1 = randint(0,height-1)
		y2 = randint(0,height-1)
		
		current_dist = dist(output_img[y1,x1],target_img[y1,x1],r_weight,g_weight,b_weight) \
					   +dist(output_img[y2,x2],target_img[y2,x2],r_weight,g_weight,b_weight)
		candidate_dist = dist(output_img[y1,x1],target_img[y2,x2],r_weight,g_weight,b_weight) \
					   +dist(output_img[y2,x2],target_img[y1,x1],r_weight,g_weight,b_weight)
			
		flip_chance = init_rand*exp(-step_count*rand_decay)
		if candidate_dist<current_dist:
			no_change_count+=1
			swap(output_img,x1,x2,y1,y2)
		else:
			no_change_count = 0
			if random()<flip_chance:
				swap(output_img,x1,x2,y1,y2)
			
		step_count+=1
	
	return output_img