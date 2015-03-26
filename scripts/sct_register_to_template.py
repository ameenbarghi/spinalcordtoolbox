#!/usr/bin/env python
#########################################################################################
#
# Register anatomical image to the template using the spinal cord centerline/segmentation.
#
# ---------------------------------------------------------------------------------------
# Copyright (c) 2013 Polytechnique Montreal <www.neuro.polymtl.ca>
# Author: Benjamin De Leener, Julien Cohen-Adad, Augustin Roux
# Modified: 2014-08-29
#
# About the license: see the file LICENSE.TXT
#########################################################################################

# TODO: make function sct_convert_binary_to_trilinear
# TODO: testing script for all cases
# TODO: try to combine seg and image based for 2nd stage
# TODO: output name file for warp using "src" and "dest" file name, i.e. warp_filesrc2filedest.nii.gz
# TODO: flag to output warping field
# TODO: check if destination is axial orientation
# TODO: set gradient-step-length in mm instead of vox size.

import sys
import getopt
import os
import commands
import time
import sct_utils as sct
from sct_orientation import get_orientation, set_orientation

# get path of the toolbox
status, path_sct = commands.getstatusoutput('echo $SCT_DIR')

# DEFAULT PARAMETERS
class Param:
    ## The constructor
    def __init__(self):
        self.debug = 0
        self.remove_temp_files = 1  # remove temporary files
        self.output_type = 1
        self.speed = 'fast'  # speed of registration. slow | normal | fast
        self.nb_iterations = '5'
        self.algo = 'SyN'
        self.gradientStep = '0.5'
        self.metric = 'MI'
        self.verbose = 1  # verbose
        self.path_template = path_sct+'/data/template'
        self.file_template = 'MNI-Poly-AMU_T2.nii.gz'
        self.file_template_label = 'landmarks_center.nii.gz'
        self.file_template_seg = 'MNI-Poly-AMU_cord.nii.gz'
        self.smoothing_sigma = 5  # Smoothing along centerline to improve accuracy and remove step effects



# MAIN
# ==========================================================================================
def main():

    # Initialization
    fname_data = ''
    fname_landmarks = ''
    fname_seg = ''
    path_template = param.path_template
    file_template = param.file_template
    file_template_label = param.file_template_label
    file_template_seg = param.file_template_seg
    output_type = param.output_type
    speed = param.speed
    param_reg = ''
    nb_iterations, algo, gradientStep, metric = param.nb_iterations, param.algo, param.gradientStep, param.metric
    remove_temp_files = param.remove_temp_files
    verbose = param.verbose
    smoothing_sigma = param.smoothing_sigma
    # start timer
    start_time = time.time()

    # get path of the toolbox
    status, path_sct = commands.getstatusoutput('echo $SCT_DIR')

    # Parameters for debug mode
    if param.debug:
        print '\n*** WARNING: DEBUG MODE ON ***\n'
        fname_data = '/Users/julien/data/temp/sct_example_data/t2_new/t2.nii.gz'
        fname_landmarks = '/Users/julien/data/temp/sct_example_data/t2_new/labels.nii.gz'
        fname_seg = '/Users/julien/data/temp/sct_example_data/t2_new/t2_seg.nii.gz'
        speed = 'superfast'
        #param_reg = '2,BSplineSyN,0.6,MeanSquares'
    else:
        # Check input parameters
        try:
            opts, args = getopt.getopt(sys.argv[1:], 'hi:l:o:p:r:s:t:')
        except getopt.GetoptError:
            usage()
        if not opts:
            usage()
        for opt, arg in opts:
            if opt == '-h':
                usage()
            elif opt in ("-i"):
                fname_data = arg
            elif opt in ('-l'):
                fname_landmarks = arg
            # elif opt in ("-m"):
            #     fname_seg = arg
            elif opt in ("-o"):
                output_type = int(arg)
            elif opt in ("-p"):
                param_reg = arg
            elif opt in ("-r"):
                remove_temp_files = int(arg)
            elif opt in ("-s"):
                fname_seg = arg
            elif opt in ("-t"):
                path_template = arg

    # display usage if a mandatory argument is not provided
    if fname_data == '' or fname_landmarks == '' or fname_seg == '':
        usage()

    # get absolute path
    path_template = os.path.abspath(path_template)

    # get fname of the template + template objects
    fname_template = sct.slash_at_the_end(path_template, 1)+file_template
    fname_template_label = sct.slash_at_the_end(path_template, 1)+file_template_label
    fname_template_seg = sct.slash_at_the_end(path_template, 1)+file_template_seg

    # check file existence
    sct.printv('\nCheck file existence...', verbose)
    sct.check_file_exist(fname_data, verbose)
    sct.check_file_exist(fname_landmarks, verbose)
    sct.check_file_exist(fname_seg, verbose)
    sct.check_file_exist(fname_template, verbose)
    sct.check_file_exist(fname_template_label, verbose)
    sct.check_file_exist(fname_template_seg, verbose)

    # print arguments
    print '\nCheck parameters:'
    print '.. Data:                 '+fname_data
    print '.. Landmarks:            '+fname_landmarks
    print '.. Segmentation:         '+fname_seg
    print '.. Path template:        '+path_template
    print '.. Output type:          '+str(output_type)
    print '.. Speed:                '+speed
    print '.. Remove temp files:    '+str(remove_temp_files)

    # Check speed parameter and create registration mode: slow 50x30, normal 50x15, fast 10x3 (default)
    if speed == "slow":
        nb_iterations = "50"
    elif speed == "normal":
        nb_iterations = "15"
    elif speed == "fast":
        nb_iterations = "5"
    elif speed == "superfast":
        nb_iterations = "1"  # only for debugging purpose-- do not inform the user about this option
    else:
        print 'ERROR: Wrong input registration speed {slow, normal, fast}.'
        sys.exit(2)

    # Check registration parameters selected by user
    if param_reg:
        nb_iterations, algo, gradientStep, metric = param_reg.split(',')

    sct.printv('\nParameters for registration:')
    sct.printv('.. Number of iterations..... '+nb_iterations)
    sct.printv('.. Algorithm................ '+algo)
    sct.printv('.. Gradient step............ '+gradientStep)
    sct.printv('.. Metric................... '+metric)

    path_data, file_data, ext_data = sct.extract_fname(fname_data)

    # create temporary folder
    print('\nCreate temporary folder...')
    path_tmp = 'tmp.'+time.strftime("%y%m%d%H%M%S")
    status, output = sct.run('mkdir '+path_tmp)

    # copy files to temporary folder
    print('\nCopy files...')
    sct.runProcess('sct_c3d '+fname_data+' -o '+path_tmp+'/data.nii')
    sct.runProcess('sct_c3d '+fname_landmarks+' -o '+path_tmp+'/landmarks.nii.gz')
    sct.runProcess('sct_c3d '+fname_seg+' -o '+path_tmp+'/segmentation.nii.gz')

    # go to tmp folder
    os.chdir(path_tmp)

    # Change orientation of input images to RPI
    print('\nChange orientation of input images to RPI...')
    set_orientation('data.nii', 'RPI', 'data_rpi.nii')
    set_orientation('landmarks.nii.gz', 'RPI', 'landmarks_rpi.nii.gz')
    set_orientation('segmentation.nii.gz', 'RPI', 'segmentation_rpi.nii.gz')

    # crop segmentation
    # output: segmentation_rpi_crop.nii.gz
    sct.runProcess('sct_crop_image -i segmentation_rpi.nii.gz -o segmentation_rpi_crop.nii.gz -dim 2 -bzmax')

    # straighten segmentation
    print('\nStraighten the spinal cord using centerline/segmentation...')
    sct.runProcess('sct_straighten_spinalcord -i segmentation_rpi_crop.nii.gz -c segmentation_rpi_crop.nii.gz -r 0')

    # Label preparation:
    # --------------------------------------------------------------------------------
    # Remove unused label on template. Keep only label present in the input label image
    print('\nRemove unused label on template. Keep only label present in the input label image...')
    sct.runProcess('sct_label_utils -t remove -i '+fname_template_label+' -o template_label.nii.gz -r landmarks_rpi.nii.gz')

    # Make sure landmarks are INT
    print '\nConvert landmarks to INT...'
    sct.runProcess('sct_c3d template_label.nii.gz -type int -o template_label.nii.gz')

    # Create a cross for the template labels - 5 mm
    print('\nCreate a 5 mm cross for the template labels...')
    sct.runProcess('sct_label_utils -t cross -i template_label.nii.gz -o template_label_cross.nii.gz -c 5')

    # Create a cross for the input labels and dilate for straightening preparation - 5 mm
    print('\nCreate a 5mm cross for the input labels and dilate for straightening preparation...')
    sct.runProcess('sct_label_utils -t cross -i landmarks_rpi.nii.gz -o landmarks_rpi_cross3x3.nii.gz -c 5 -d')

    # Apply straightening to labels
    print('\nApply straightening to labels...')
    sct.runProcess('sct_apply_transfo -i landmarks_rpi_cross3x3.nii.gz -o landmarks_rpi_cross3x3_straight.nii.gz -d segmentation_rpi_crop_straight.nii.gz -w warp_curve2straight.nii.gz -x nn')

    # Convert landmarks from FLOAT32 to INT
    print '\nConvert landmarks from FLOAT32 to INT...'
    sct.runProcess('sct_c3d landmarks_rpi_cross3x3_straight.nii.gz -type int -o landmarks_rpi_cross3x3_straight.nii.gz')

    # Estimate affine transfo: straight --> template (landmark-based)'
    print '\nEstimate affine transfo: straight anat --> template (landmark-based)...'
    sct.runProcess('sct_ANTSUseLandmarkImagesToGetAffineTransform template_label_cross.nii.gz landmarks_rpi_cross3x3_straight.nii.gz affine straight2templateAffine.txt')

    # Apply affine transformation: straight --> template
    print '\nApply affine transformation: straight --> template...'
    sct.runProcess('sct_apply_transfo -i data_rpi.nii -o data_rpi_straight2templateAffine.nii -d '+fname_template+' -w warp_curve2straight.nii.gz,straight2templateAffine.txt')
    sct.runProcess('sct_apply_transfo -i segmentation_rpi.nii.gz -o segmentation_rpi_straight2templateAffine.nii.gz -d '+fname_template+' -w warp_curve2straight.nii.gz,straight2templateAffine.txt -x nn')

    # Registration straight spinal cord to template
    print('\nRegister straight spinal cord to template...')
    # register using segmentations
    sct.runProcess('sct_register_multimodal -i segmentation_rpi_straight2templateAffine.nii.gz -d '+fname_template_seg+' -a bsplinesyn -p 10,1,0,0.5,MeanSquares -r 0 -v '+str(verbose)+' -x nn -z 10', verbose)
    # apply to image
    sct.runProcess('sct_apply_transfo -i data_rpi_straight2templateAffine.nii -w warp_segmentation_rpi_straight2templateAffine2MNI-Poly-AMU_cord.nii.gz -d '+fname_template+' -o data_rpi_straight2templateAffine_step0.nii')
    # register using images
    sct.runProcess('sct_register_multimodal -i data_rpi_straight2templateAffine_step0.nii -d '+fname_template+' -a syn -p 10,1,0,0.5,MI -r 0 -v '+str(verbose)+' -x spline -z 10', verbose)

    # Concatenate transformations: template2anat & anat2template
    sct.printv('\nConcatenate transformations: template --> straight --> anat...', verbose)
    sct.runProcess('sct_concat_transfo -w warp_MNI-Poly-AMU_T22data_rpi_straight2templateAffine_step0.nii.gz,warp_MNI-Poly-AMU_cord2segmentation_rpi_straight2templateAffine.nii.gz,-straight2templateAffine.txt,warp_straight2curve.nii.gz -d data.nii -o warp_template2anat.nii.gz')
    sct.printv('\nConcatenate transformations: anat --> straight --> template...', verbose)
    sct.runProcess('sct_concat_transfo -w warp_curve2straight.nii.gz,straight2templateAffine.txt,warp_segmentation_rpi_straight2templateAffine2MNI-Poly-AMU_cord.nii.gz,warp_data_rpi_straight2templateAffine_step02MNI-Poly-AMU_T2.nii.gz -d '+fname_template+' -o warp_anat2template.nii.gz')

    # Apply warping fields to anat and template
    if output_type == 1:
        sct.runProcess('sct_apply_transfo -i '+fname_template+' -o template2anat.nii.gz -d data.nii -w warp_template2anat.nii.gz')
        sct.runProcess('sct_apply_transfo -i data.nii  -o anat2template.nii.gz -d '+fname_template+' -w warp_anat2template.nii.gz')

    # come back to parent folder
    os.chdir('..')

   # Generate output files
    sct.printv('\nGenerate output files...', verbose)
    sct.generate_output_file(path_tmp+'/warp_template2anat.nii.gz', 'warp_template2anat.nii.gz')
    sct.generate_output_file(path_tmp+'/warp_anat2template.nii.gz', 'warp_anat2template.nii.gz')
    if output_type == 1:
        sct.generate_output_file(path_tmp+'/template2anat.nii.gz', 'template2anat'+ext_data)
        sct.generate_output_file(path_tmp+'/anat2template.nii.gz', 'anat2template'+ext_data)

    # Delete temporary files
    if remove_temp_files == 1:
        sct.printv('\nDelete temporary files...', verbose)
        sct.runProcess('rm -rf '+path_tmp)

    # display elapsed time
    elapsed_time = time.time() - start_time
    sct.printv('\nFinished! Elapsed time: '+str(int(round(elapsed_time)))+'s', verbose)

    # to view results
    sct.printv('\nTo view results, type:', verbose)
    sct.printv('fslview '+fname_data+' template2anat -b 0,4000 &', verbose, 'info')
    sct.printv('fslview '+fname_template+' -b 0,5000 anat2template &\n', verbose, 'info')


# Print usage
# ==========================================================================================
def usage():
    print """
"""+os.path.basename(__file__)+"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Part of the Spinal Cord Toolbox <https://sourceforge.net/projects/spinalcordtoolbox>

DESCRIPTION
  Register anatomical image to the template.

USAGE
  """+os.path.basename(__file__)+""" -i <anat> -m <segmentation> -l <landmarks>

MANDATORY ARGUMENTS
  -i <anat>                    anatomical image
  -s <segmentation>            spinal cord segmentation.
  -l <landmarks>               landmarks at spinal cord center.
                               See: http://sourceforge.net/p/spinalcordtoolbox/wiki/create_labels/

OPTIONAL ARGUMENTS
  -o {0, 1}                    output type. 0: warp, 1: warp+images. Default="""+str(param_default.output_type)+"""
  -p <param>                   parameters to register the straightened anat to the template.
                               Separate with comma. Default="""+param_default.nb_iterations+','+param_default.algo+','+param_default.gradientStep+','+param_default.metric+"""
                                 1) number of iterations.
                                 2) algo: {syn, bsplinesyn}
                                 3) gradient step. The larger the more deformation.
                                 4) metric: {MI,MeanSquares}.
                                    If you find very large deformations, switching to MeanSquares can help.
  -t <path_template>           Specify path to template. Default="""+str(param_default.path_template)+"""
  -r {0, 1}                    remove temporary files. Default="""+str(param_default.remove_temp_files)+"""
  -h                           help. Show this message

EXAMPLE
  """+os.path.basename(__file__)+""" -i t2.nii.gz -l labels.nii.gz -s t2_seg.nii.gz\n"""

    # exit program
    sys.exit(2)



# START PROGRAM
# ==========================================================================================
if __name__ == "__main__":
    # initialize parameters
    param = Param()
    param_default = Param()
    # call main function
    main()
