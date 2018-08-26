from __future__ import division,print_function
import numpy as np
from colorsys import rgb_to_yiq

def pixel_sort(input_img,target_img,verbose=True):
	if verbose:
		print('Sorting pixels...')

	height,width,_ = target_img.shape
	row_indices = np.array([[i]*width for i in range(height)])
	col_indices = np.array([range(width) for i in range(height)])
	row_indices = np.reshape(row_indices,[height,width,1])
	col_indices = np.reshape(col_indices,[height,width,1])
	
	luma_input = np.apply_along_axis(lambda x: rgb_to_yiq(*x)[0],2,input_img)
	luma_input = np.reshape(luma_input,[height,width,1])
	luma_input = np.concatenate([luma_input,row_indices,col_indices],axis=2)
	luma_input = np.reshape(luma_input,[-1,3])
	luma_input = luma_input[luma_input[:,0].argsort()]
	
	luma_target = np.apply_along_axis(lambda x: rgb_to_yiq(*x)[0],2,target_img)
	luma_target = np.reshape(luma_target,[height,width,1])
	luma_target = np.concatenate([luma_target,row_indices,col_indices],axis=2)
	luma_target = np.reshape(luma_target,[-1,3])
	luma_target = luma_target[luma_target[:,0].argsort()]
	
	output_img = np.zeros([height,width,3])
	for i in range(luma_target.shape[0]):
		output_img[int(luma_target[i,1]),int(luma_target[i,2]),:] = \
			input_img[int(luma_input[i,1]),int(luma_input[i,2]),:]
	return output_img.astype('uint8')