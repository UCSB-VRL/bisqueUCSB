import os

def isvalid(args):
	## Validations
	if not os.path.exists(args.input_fname):
	    print('Error: ' + args.input_fname + ' does not exist.')
	    return False

	if not os.path.exists(args.model_fname_sr_detector):
	    print('Error: ' + args.model_fname_sr_detector + ' does not exist.')
	    return False

	if not (args.model_fname_sr_detector.lower().endswith('.h5')):
	    print('Error: Only ".h5" files are supported to represent the deep learning models.')
	    return False

	if not os.path.exists(args.model_fname_si_detector):
	    print('Error: ' + args.model_fname_si_detector + ' does not exist.')
	    return False

	if not (args.model_fname_si_detector.lower().endswith('.h5')):
	    print('Error: Only ".h5" files are supported to represent the deep learning models.')
	    return False

	if not os.path.exists(args.model_fname_stage2):
	    print('Error: ' + args.model_fname_stage2 + ' does not exist.')
	    return False

	if not (args.model_fname_stage2.lower().endswith('.h5')):
	    print('Error: Only ".h5" files are supported to represent the deep learning models.')
	    return False

	return True
