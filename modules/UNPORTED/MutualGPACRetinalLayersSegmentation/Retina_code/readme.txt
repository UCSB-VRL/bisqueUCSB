Overview:
	all files needed for retinal segmentation are contained in this folder

	main scripts(associated function):    

	m_segment.m		segments retinal images & saves results
	m_evaluation.m 		finds the average distance between ground truth & segmentation boundaries
	m_mask.m		creates masks of the segmentation
	m_get_fmeasure.m	finds the f-measure of ground truth and segmentation masks

	

1) To segment all the retina images Nhat used to test his algorithm use:	m_segment.m
	
m_segment calls f_segment which calls f_example which uses multiple functions itself all of which are contained in this folder. 

If you wish to segment only one layer of one image, you can use f_example, but Nhat's data was produce by running the algorithm for each image several times with different training images. 


2) To find the avg_distance between boundaries in the segmentation use:  m_evaluation.m


3) To create the masks need for finding the f_measure in part 4 (below) use m_mask.m
    	m_mask.m creates a several masks for every image segmented. The procedure is to use every image in a subgroup as a training image for all the other images. This means that if there are 5 images in a subgroup, then each has four masks.


4) To find the weighted f-measure use: m_get_fmeasure.m
	m_get_fmeasure.m uses f_get_fmeasure.m which uses f_measure_warea.m 

	if you want to get the fmeasure, you can use f_measure_warea.m by itself. m_get_fmeasure.m computes the numbers for Nhat Vu's segmentation algorithm as they are presently saved.

	Please note that m_get_fmeasure.m calculates the fmeasure by taking each mask made from an image (see 3 above), comparing it to the ground truth, getting an f_measure, averaging all the f-measures for a subgroup together. 



jmhfreire@gmail.com
jose freire 8/22/07
