#!/usr/bin/env python
########################################################################################################################
#
#
# Utility functions useed for the segmentation of the gray matter
#
# ----------------------------------------------------------------------------------------------------------------------
# Copyright (c) 2014 Polytechnique Montreal <www.neuro.polymtl.ca>
# Author: Sara Dupont
# Modified: 2015-03-24
#
# About the license: see the file LICENSE.TXT
########################################################################################################################

from math import sqrt

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
# import time
# from scipy.optimize import minimize

from msct_image import Image
import sct_utils as sct
from msct_parser import Parser


class Slice:
    """
    Slice instance used in the model dictionary for the segmentation of the gray matter
    """
    def __init__(self, slice_id=None, im=None, seg=None, reg_to_m=None, im_m=None, seg_m=None,
                 im_m_flat=None, seg_m_flat=None, level=None):
        """
        Slice constructor

        :param slice_id: slice ID number, type: int

        :param im: original image (a T2star 2D image croped around the spinal cord), type: numpy array

        :param seg: manual segmentation of the original image, type: numpy array

        :param reg_to_m: name of the file containing the transformation for this slice to go
        from the image original space to the model space, type: string

        :param im_m: image in the model space, type: numpy array

        :param seg_m: manual segmentation in the model space, type: numpy array

        :param im_m_flat: flatten image in the model space, type: numpy array

        :param seg_m_flat: flatten manual segmentation in the model space, type: numpy array

        :param level: spinal AND\OR ? vertebral level of the slice, type: ??

        **WARNING : the level isn't used yet in the gm segmentation method**
        """
        self.id = slice_id
        self.im = im
        self.seg = seg
        self.reg_to_M = reg_to_m
        self.im_M = im_m
        self.seg_M = seg_m
        self.im_M_flat = im_m_flat
        self.seg_M_flat = seg_m_flat
        self.level = level

    def set(self, slice_id=None, im=None, seg=None, reg_to_m=None, im_m=None, seg_m=None,
            im_m_flat=None, seg_m_flat=None, level=None):
        """
        Slice setter, only the specified parameters are set

        :param slice_id: slice ID number, type: int

        :param im: original image (a T2star 2D image croped around the spinal cord), type: numpy array

        :param seg: manual segmentation of the original image, type: numpy array

        :param reg_to_m: name of the file containing the transformation for this slice to go
        from the image original space to the model space, type: string

        :param im_m: image in the model space, type: numpy array

        :param seg_m: manual segmentation in the model space, type: numpy array

        :param im_m_flat: flatten image in the model space, type: numpy array

        :param seg_m_flat: flatten manual segmentation in the model space, type: numpy array

        :param level: spinal AND\OR ? vertebral level of the slice, type: ??

        **WARNING : the level isn't used yet in the gm segmentation method**
        """
        if slice_id is not None:
            self.id = slice_id
        if im is not None:
            self.im = im
        if seg is not None:
            self.seg = seg
        if reg_to_m is not None:
            self.reg_to_M = reg_to_m
        if im_m is not None:
            self.im_M = im_m
        if seg_m is not None:
            self.seg_M = seg_m
        if im_m_flat is not None:
            self.im_M_flat = im_m_flat
        if seg_m_flat is not None:
            self.seg_M_flat = seg_m_flat
        if level is not None:
            self.level = level

    def __repr__(self):
        s = '\nSlice #' + str(self.id)
        if self.level is not None:
            s += 'Level : ' + str(self.level)
        s += '\nAtlas : \n' + str(self.im) + '\nDecision : \n' + str(self.seg) +\
             '\nTransformation to model space : ' + self.reg_to_M
        if self.im_M is not None:
            s += '\nAtlas in the common model space: \n' + str(self.im_M)
        if self.seg_M is not None:
            s += '\nDecision in the common model space: \n' + str(self.seg_M)
        return s


########################################################################################################################
# ---------------------------------------------------- FUNCTIONS ----------------------------------------------------- #
########################################################################################################################

'''
# ----------------------------------------------------------------------------------------------------------------------
def split(slice):
    """
    Split a given slice in two

    :param slice: slice to split, type: numpy array
    :return:
    """
    left_slice = []
    right_slice = []
    column_length = slice.shape[1]
    i = 0
    for column in slice:
        if i < column_length / 2:
            left_slice.append(column)
        else:
            right_slice.insert(0, column)
        i += 1
    left_slice = np.asarray(left_slice)
    right_slice = np.asarray(right_slice)
    assert (left_slice.shape == right_slice.shape), \
        str(left_slice.shape) + '==' + str(right_slice.shape) + \
        'You should check that the first dim of your image (or slice) is an odd number'
    return left_slice, right_slice
'''


# ----------------------------------------------------------------------------------------------------------------------
def show(coord_projected_img, pca, target):
    """
    Display an image projected in the reduced PCA space

    :param coord_projected_img: Coordinates of the target image in the PCA reduced space

    :param pca: PCA instance (used to get the mean image)

    :param target: image to display
    """
    import copy

    img_reduced_space = copy.copy(pca.mean_image)
    for i in range(0, coord_projected_img.shape[0]):
        img_reduced_space += int(coord_projected_img[i][0]) * pca.kept_modes.T[i].reshape(pca.N, 1)

    n = int(sqrt(pca.N))
    imgplot = plt.imshow(pca.mean_image)
    imgplot.set_interpolation('nearest')
    imgplot.set_cmap('gray')
    plt.title('Mean PCA Image')
    plt.show()

    imgplot = plt.imshow(target.reshape(n, n))
    imgplot.set_interpolation('nearest')
    # imgplot.set_cmap('gray')
    plt.title('Original Image')
    plt.show()

    imgplot = plt.imshow(img_reduced_space.reshape(n, n))
    imgplot.set_interpolation('nearest')
    # imgplot.set_cmap('gray')
    plt.title('Projected Image (projected in the PCA reduced space)')
    plt.show()


# ----------------------------------------------------------------------------------------------------------------------
def save_image(im_array, im_name, path='', im_type='', verbose=1):
    """
    Save an image from an array,
    if the array is a flatten image, the saved image will be square shaped

    :param im_array: image to save

    :param im_name: name of the image

    :param path: path where to save it

    :param im_type: type of image

    :param verbose:
    """
    if isinstance(im_array, list):
        n = int(sqrt(len(im_array)))
        im_data = np.asarray(im_array).reshape(n, n)
    else:
        im_data = np.asarray(im_array)
    im = Image(param=im_data, verbose=verbose)
    im.file_name = im_name
    im.ext = '.nii.gz'
    if path != '':
        im.path = path
    im.save(type=im_type)


# ----------------------------------------------------------------------------------------------------------------------
def apply_ants_transfo(fixed_im, moving_im, search_reg=True, transfo_type='Rigid', apply_transfo=True, transfo_name='',
                       binary=True, path='./', inverse=0, verbose=0):
    """
    Compute and/or apply a registration using ANTs

    :param fixed_im: fixed image for the registration, type: numpy array

    :param moving_im: moving image for the registration, type: numpy array

    :param search_reg: compute (search) or load (from a file) the transformation to do, type: boolean

    :param transfo_type: type of transformation to apply, type: string

    :param apply_transfo: apply or not the transformation, type: boolean

    :param transfo_name: name of the file containing the transformation information (to load or save the transformation,
     type: string

    :param binary: if the image to register is binary, type: boolean

    :param path: path where to load/save the transformation

    :param inverse: apply inverse transformation

    :param verbose: verbose
    """
    import time
    res_im = None
    try:
        transfo_dir = transfo_type.lower() + '_transformations'
        if transfo_dir not in os.listdir(path):
            sct.run('mkdir ' + path + transfo_dir)
        dir_name = 'tmp_reg_' + str(time.time())
        sct.run('mkdir ' + dir_name, verbose=verbose)
        os.chdir('./' + dir_name)

        if binary:
            t = 'uint8'
        else:
            t = ''

        fixed_im_name = 'fixed_im'
        save_image(fixed_im, fixed_im_name, im_type=t, verbose=verbose)
        moving_im_name = 'moving_im'
        save_image(moving_im, moving_im_name, im_type=t, verbose=verbose)

        mat_name, inverse_mat_name = find_ants_transfo_name(transfo_type)

        if search_reg:
            reg_interpolation = 'BSpline'
            transfo_params = ''
            if transfo_type == 'BSpline':
                transfo_params = ',1'
            elif transfo_type == 'BSplineSyN':
                transfo_params = ',1,1'
            elif transfo_type == 'SyN':
                transfo_params = ',1,1'
            gradientstep = 0.3  # 0.5
            metric = 'MeanSquares'
            metric_params = ',5'
            # metric = 'MI'
            # metric_params = ',1,2'
            niter = 20
            smooth = 0
            shrink = 1
            cmd_reg = 'sct_antsRegistration -d 2 -n ' + reg_interpolation + ' -t ' + transfo_type + '[' + str(gradientstep) + transfo_params + '] ' \
                      '-m ' + metric + '[' + fixed_im_name + '.nii.gz,' + moving_im_name + '.nii.gz ' + metric_params + '] -o reg  -c ' + str(niter) + \
                      ' -s ' + str(smooth) + ' -f ' + str(shrink) + ' -v ' + str(verbose)

            sct.run(cmd_reg, verbose=verbose)

            sct.run('cp ' + mat_name + ' ../' + path + transfo_dir + '/'+transfo_name, verbose=verbose)
            if transfo_type == 'SyN':
                sct.run('cp ' + inverse_mat_name + ' ../' + path + transfo_dir + '/'+transfo_name + '_inversed',
                        verbose=verbose)

        if apply_transfo:
            if not search_reg:
                sct.run('cp ../' + path + transfo_dir + '/' + transfo_name + ' ./' + mat_name, verbose=verbose)
                if transfo_type == 'SyN':
                    sct.run('cp ../' + path + transfo_dir + '/' + transfo_name + '_inversed' + ' ./' + inverse_mat_name,
                            verbose=verbose)

            if binary:
                apply_transfo_interpolation = 'NearestNeighbor'
            else:
                apply_transfo_interpolation = 'BSpline'

            if transfo_type == 'SyN' and inverse:
                cmd_apply = 'sct_antsApplyTransforms -d 2 -i ' + moving_im_name + '.nii.gz -o ' + moving_im_name + '_moved.nii.gz ' \
                            '-n ' + apply_transfo_interpolation + ' -t [' + inverse_mat_name + '] ' \
                            '-r ' + fixed_im_name + '.nii.gz -v ' + str(verbose)

            else:
                cmd_apply = 'sct_antsApplyTransforms -d 2 -i ' + moving_im_name + '.nii.gz -o ' + moving_im_name + '_moved.nii.gz ' \
                            '-n ' + apply_transfo_interpolation + ' -t [' + mat_name + ',' + str(inverse) + '] ' \
                            '-r ' + fixed_im_name + '.nii.gz -v ' + str(verbose)

            sct.run(cmd_apply, verbose=verbose)

            res_im = Image(moving_im_name + '_moved.nii.gz')
    except Exception, e:
        sct.printv('WARNING: AN ERROR OCCURRED WHEN DOING RIGID REGISTRATION USING ANTs', 1, 'warning')
        print e
    else:
        sct.printv('Removing temporary files ...', verbose=verbose, type='normal')
        os.chdir('..')
        sct.run('rm -rf ' + dir_name + '/', verbose=verbose)

    if apply_transfo and res_im is not None:
        return res_im.data


# ----------------------------------------------------------------------------------------------------------------------
def find_ants_transfo_name(transfo_type):
    """
    find the name of the transformation file automatically saved by ANTs for a type of transformation

    :param transfo_type: type of transformation

    :return transfo_name, inverse_transfo_name:
    """
    transfo_name = ''
    inverse_transfo_name = ''
    if transfo_type == 'Rigid' or transfo_type == 'Affine':
        transfo_name = 'reg0GenericAffine.mat'
    elif transfo_type == 'BSpline':
        transfo_name = 'reg0BSpline.txt'
    elif transfo_type == 'BSplineSyN' or transfo_type == 'SyN':
        transfo_name = 'reg0Warp.nii.gz'
        inverse_transfo_name = 'reg0InverseWarp.nii.gz'
    return transfo_name, inverse_transfo_name


#######################  DEVELOPING GROUPWISE  #######################
# ----------------------------------------------------------------------------------------------------------------------
def apply_2d_transformation(matrix, tx=0, ty=0, theta=0, scx=1, scy=1, transfo=None, inverse=False):
    """
    Apply an Affine transformation defined a translation, a rotation and a scaling

    :param matrix: image to apply transformation on, type: numpy ndarray

    :param tx: translation along the x-axis, type: float

    :param ty: translation along the y-axis, type: float

    :param theta: rotation angle in counter-clockwise direction as radians, type: float

    :param scx: scaling factor along the x-axis, type: float

    :param scy: scaling factor along the y-axis, type: float

    :return transformed_mat, transfo: transformed matrix, transformation used
    """
    from skimage import transform as tf
    if transfo is None:
        transfo = tf.AffineTransform(scale=[scx, scy], rotation=theta, translation=(tx, ty))

    if inverse:
        transformed_mat = tf.warp(matrix.astype('uint32'), transfo.inverse, preserve_range=True)
    else:
        transformed_mat = tf.warp(matrix.astype('uint32'), transfo, preserve_range=True)

    return transformed_mat, transfo


# ----------------------------------------------------------------------------------------------------------------------
def kronecker_delta(x, y):
    """
    Kronecker delta function
    :param x: float
    :param y: float
    :return: 0 if x=y, 1 if x and y are different
    """
    if x == y:
        return 1
    else:
        return 0


'''
# ------------------------------------------------------------------------------------------------------------------
def compute_mutual_information_seg(seg_data_set):
    """
    Compute the mean segmentation image for a given segmentation data set
    keeping only the pixels that are present in ALL the data set
    :param seg_data_set:
    :return:
    """
    seg_sum = np.asarray(seg_data_set[0])
    n_seg = len(seg_data_set)

    for dic_slice in seg_data_set[1:]:
        seg_sum += np.asarray(dic_slice)

    index_to_keep = seg_sum == n_seg
    mean_seg = index_to_keep.astype(int)

    return mean_seg
'''


# ------------------------------------------------------------------------------------------------------------------
def l0_norm(x, y):
    """
    L0 norm of two images x and y
    :param x:
    :param y:
    :return: l0 norm
    """
    return np.linalg.norm(x.flatten() - y.flatten(), 0)


# ------------------------------------------------------------------------------------------------------------------
def inverse_wmseg_to_gmseg(wm_seg, original_im, name_wm_seg):
    """
    Inverse a white matter segmentation array image to get a gray matter segmentation image and save it

    :param wm_seg: white matter segmentation to inverse, type: Image

    :param original_im: original image croped around the spinal cord

    :param name_wm_seg: name of the white matter segmentation (to save the associated gray matter segmentation),
     type: string

    :return inverted_seg: gray matter segmentation array
    """
    import copy

    inverted_seg = []
    sc = Image(param=original_im.data)
    nz_coord_sc = sc.getNonZeroCoordinates()
    for coord in nz_coord_sc:
        sc.data[coord.x, coord.y, coord.z] = 1
    sc.file_name = 'original_target_sc'
    sc.ext = '.nii.gz'
    sc.save()

    # erosion of the spinal cord segmentation
    new_sc_dat = copy.deepcopy(sc.data)

    for i_slice, sc_slice in enumerate(sc.data):
        for i_row, row in enumerate(sc_slice):
            for i_pix, pix in enumerate(row):
                if pix == 1:
                    if row[i_pix-1] == 0 or row[i_pix+1] == 0 \
                            or sc_slice[i_row+1, i_pix] == 0 or sc_slice[i_row-1, i_pix] == 0:
                        new_sc_dat[i_slice, i_row, i_pix] = 0

    for seg_slice, sc_slice in zip(wm_seg.data, new_sc_dat):
        inverted_seg.append(sc_slice-seg_slice)

    inverted_seg_pos = (np.asarray(inverted_seg) > 0).astype(int)

    inverted_seg_pos_image = Image(param=np.asarray(inverted_seg_pos))
    inverted_seg_pos_image.file_name = name_wm_seg + '_inv_to_gm'
    inverted_seg_pos_image.ext = '.nii.gz'
    inverted_seg_pos_image.save()

    return inverted_seg_pos


# ------------------------------------------------------------------------------------------------------------------
def inverse_gmseg_to_wmseg(gm_seg, original_im, name_gm_seg):
    """
    Inverse a gray matter segmentation array image to get a white matter segmentation image and save it

    :param gm_seg: gray matter segmentation to inverse, type: Image

    :param original_im: original image croped around the spinal cord

    :param name_gm_seg: name of the gray matter segmentation (to save the associated white matter segmentation),
     type: string

    :return inverted_seg: white matter segmentation array
    """
    gm_seg_copy = gm_seg.copy()
    sc = original_im.copy()
    nz_coord_sc = sc.getNonZeroCoordinates()

    nz_coord_seg = gm_seg.getNonZeroCoordinates()
    for coord in nz_coord_sc:
        sc.data[coord.x, coord.y, coord.z] = 1
    for coord in nz_coord_seg:
        gm_seg_copy.data[coord.x, coord.y, coord.z] = 1
    # cast of the -1 values (-> GM pixel at the exterior of the SC pixels) to +1 --> WM pixel
    res_wm_seg = np.absolute(sc.data - gm_seg_copy.data).astype(int)

    res_wm_seg_im = Image(param=np.asarray(res_wm_seg), absolutepath=name_gm_seg + '_inv_to_wm.nii.gz')
    res_wm_seg_im.save()

    return res_wm_seg


# ------------------------------------------------------------------------------------------------------------------
def compute_majority_vote_mean_seg(seg_data_set, threshold=0.5):
    """
    Compute the mean segmentation image for a given segmentation data set seg_data_set by Majority Vote

    :param seg_data_set: data set of segmentation slices (2D)

    :param threshold: threshold to select the value of a pixel
    :return:
    """
    return (np.sum(seg_data_set, axis=0) / float(len(seg_data_set)) >= threshold).astype(int)

########################################################################################################################
# -------------------------------------------------- PRETREATMENTS --------------------------------------------------- #
########################################################################################################################


# ------------------------------------------------------------------------------------------------------------------
def crop_t2_star(path):
    for subject_dir in os.listdir(path):
        if os.path.isdir(subject_dir):
            t2star = ''
            sc_seg = ''
            seg_in = ''
            seg_in_name = ''
            manual_seg = ''
            manual_seg_name = ''
            mask_box = ''
            seg_in_croped = ''
            manual_seg_croped = ''

            # print subject_dir

            '''
            # VERSION 1 OF THE PRE TREATMENTS

            mask_centerline = ''
            centerline = ''
            mask_box = ''
            croped = ''
            print subject_dir
            for file in os.listdir(dir + '/' + subject_dir):
                if 't2star.nii' in file and 'mask' not in file:
                    t2star = file
                elif '-mask_centerline.nii' in file:
                    mask_centerline = file
                elif 'mask_' in file:
                    mask_box = file
                elif '_centerline.nii' in file:
                    centerline = file
                elif '_croped' in file :
                    croped = file
            if t2star != '' and mask_centerline != '':
                path = dir + '/' + subject_dir + '/'
                print 'path : ', path
                os.chdir(path)
                t2star_path,t2star_name,ext = sct.extract_fname(t2star)
                if centerline == '':
                    sct.run('sct_get_centerline -i ' + t2star + ' -p '  + mask_centerline)
                if mask_box == '':
                    sct.run('sct_create_mask -i '  + t2star + ' -m centerline,'  + centerline +' -s 40 -f box' )
                if croped == '':
                    sct.run('sct_crop_image -i '  + t2star + ' -o '  + t2star_name + '_croped' + ext+
                    ' -m mask_' + t2star)
                os.chdir('..')
            '''

            '''
            # VERSION 2 OF THE PRE TREATMENTS



            for file in os.listdir(dir + '/' + subject_dir):
                if 't2star.nii' in file and 'mask' not in file and 'seg' not in file and 'IRP' not in file:
                    t2star = file
                    t2star_path,t2star_name,ext = sct.extract_fname(t2star)
                elif 'square_mask' in file and 'IRP' not in file:
                    mask_box = file
                elif '_seg' in file and 'in' not in file and 'croped' not in file and 'IRP' not in file:
                    sc_seg = file
                elif '_seg_in' in file and 'croped' not in file and 'IRP' not in file:
                    seg_in = file
                    seg_in_name = sct.extract_fname(seg_in)[1]
                elif '_croped' in file and 'IRP' not in file:
                    seg_in_croped = file
            if t2star != '' and sc_seg != '':
                path = dir + '/' + subject_dir + '/'
                print 'path : ', path
                os.chdir(path)

                try:

                    if seg_in == '':
                        sct.run('sct_crop_over_mask.py -i ' + t2star + ' -mask ' + sc_seg + ' -square 0 -o '
                        + t2star_name + '_seg_in')
                        seg_in = t2star_name + '_seg_in.nii.gz'
                        seg_in_name = t2star_name + '_seg_in'
                    if mask_box == '':
                        sct.run('sct_create_mask -i ' + t2star + ' -m center -s 70 -o '
                         + t2star_name + '_square_mask.nii.gz -f box' )
                        mask_box = t2star_name + '_square_mask.nii.gz'
                    if seg_in_croped == '':
                        sct.run('sct_crop_over_mask.py -i ' + seg_in + ' -mask ' + mask_box + ' -square 1 -o '
                        + seg_in_name + '_croped')
                    #os.chdir('..')

                except Exception,e:
                    sct.printv('WARNING: an error occured ... \n ' + str(e) ,1, 'warning')
                else:
                    print 'Done !'
                    #sct.run('rm -rf ./tmp_' + now)
                os.chdir('..')
            '''

            # VERSION 3 OF THE PRE TREATMENTS
            for subject_file in os.listdir(path + '/' + subject_dir):
                file_low = subject_file.lower()
                if 't2star.nii' in file_low and 'mask' not in file_low and 'seg' not in file_low \
                        and 'IRP' not in file_low:
                    t2star = subject_file
                    t2star_path, t2star_name, ext = sct.extract_fname(t2star)
                elif 'square' in file_low and 'mask' in file_low and 'IRP' not in file_low:
                    mask_box = subject_file
                elif '_seg' in file_low and 'in' not in file_low and 'croped' not in file_low and 'gm' not in file_low \
                        and 'IRP' not in file_low:
                    sc_seg = subject_file
                elif '_seg_in' in file_low and 'croped' not in file_low and 'IRP' not in file_low:
                    seg_in = subject_file
                    seg_in_name = sct.extract_fname(seg_in)[1]
                elif 'gm' in file_low and 'croped.nii' not in file_low and 'IRP' not in file_low:
                    manual_seg = subject_file
                    print manual_seg
                    manual_seg_name = sct.extract_fname(manual_seg)[1]
                elif '_croped.nii' in file_low and 'IRP' not in file_low and 'gm' not in file_low:
                    seg_in_croped = subject_file
                elif '_croped.nii' in file_low and 'gm' in file_low and 'IRP' not in file_low:
                    manual_seg_croped = subject_file
                    print manual_seg_croped
            if t2star != '' and sc_seg != '':
                path = path + '/' + subject_dir + '/'
                print 'path : ', path
                os.chdir(path)
                '''
                now = str(time.time())
                sct.run('mkdir tmp_'+ now)
                sct.run('cp ./' + t2star + ' ./tmp_'+now+'/'+t2star)
                sct.run('cp ./' + sc_seg + ' ./tmp_'+now+'/'+sc_seg)
                os.chdir('./tmp_'+now)
                '''
                try:

                    if seg_in == '':
                        sct.run('sct_crop_over_mask.py -i ' + t2star + ' -mask ' + sc_seg + ' -square 0 '
                                '-o ' + t2star_name + '_seg_in')
                        seg_in = t2star_name + '_seg_in.nii.gz'
                        seg_in_name = t2star_name + '_seg_in'

                    if mask_box == '':
                        '''
                        sct.run('sct_create_mask -i ' + t2star + ' -m center -s 70'
                                ' -o ' + t2star_name + '_square_mask.nii.gz -f box' )
                        '''

                        sct.run('sct_create_mask -i ' + seg_in + ' -m centerline,' + sc_seg + ' -s 43 '
                                '-o ' + t2star_name + '_square_mask_from_sc_seg.nii.gz -f box')
                        mask_box = t2star_name + '_square_mask_from_sc_seg.nii.gz'

                    if seg_in_croped == '':
                        sct.run('sct_crop_over_mask.py -i ' + seg_in + ' -mask ' + mask_box + ' -square 1 '
                                '-o ' + seg_in_name + '_croped')

                    if manual_seg_croped == '':
                        sct.run('sct_crop_over_mask.py -i ' + manual_seg + ' -mask ' + mask_box + ' -square 1'
                                ' -o ' + manual_seg_name + '_croped')

                    # os.chdir('..')

                except Exception, e:
                    sct.printv('WARNING: an error occured ... \n ' + str(e), 1, 'warning')
                else:
                    print 'Done !'
                    # sct.run('rm -rf ./tmp_' + now)
                os.chdir('..')


########################################################################################################################
# -------------------------------------------------- LEAVE ONE OUT --------------------------------------------------- #
########################################################################################################################

# ------------------------------------------------------------------------------------------------------------------
def leave_one_out(dic_path, reg=None):
    import time
    dice_file = open('dice_coeff.txt', 'w')
    dice_sum = 0
    time_file = open('computation_time.txt', 'w')
    time_sum = 0
    n_subject = 0
    n_slices = 0
    e = None
    error_map_sum = None
    error_map_abs_sum = None
    first = True

    for subject_dir in os.listdir(dic_path):
        subject_path = dic_path + '/' + subject_dir
        if os.path.isdir(subject_path):
            try:
                tmp_dir = 'tmp_' + subject_dir + '_as_target'
                sct.run('mkdir ' + tmp_dir)

                tmp_dic_name = 'dic'
                sct.run('cp -r ' + dic_path + ' ./' + tmp_dir + '/' + tmp_dic_name + '/')
                sct.run('mv ./' + tmp_dir + '/' + tmp_dic_name + '/' + subject_dir + ' ./' + tmp_dir)

                # Gray matter segmentation using this subject as target
                os.chdir(tmp_dir)
                target = ''
                ref_gm_seg = ''
                res = ''

                for file_name in os.listdir(subject_dir):
                    if 'seg_in' in file_name:
                        target = subject_dir + '/' + file_name
                    elif 'manual' in file_name:
                        ref_gm_seg = subject_dir + '/' + file_name

                cmd_gm_seg = 'sct_asman -i ' + target + ' -dic ' + tmp_dic_name + ' -model compute'
                if reg is not None:
                    cmd_gm_seg += ' -reg ' + reg

                before_seg = time.time()
                sct.run(cmd_gm_seg)
                seg_time = time.time() - before_seg

                for file_name in os.listdir('.'):
                    if 'graymatterseg' in file_name and 'manual' not in file_name:
                        res = file_name

                # Validation
                ref_gm_seg_im = Image(ref_gm_seg)
                target_im = Image(target)

                inverse_gmseg_to_wmseg(ref_gm_seg_im, target_im, ref_gm_seg_im.file_name)

                ref_wm_seg = ref_gm_seg_im.file_name + '_inv_to_wm.nii.gz'
                ref_wm_seg_im = Image(ref_wm_seg)

                res_im = Image(res)

                # Dice coefficient
                status, dice_output = sct.run('sct_dice_coefficient ' + res + ' ' + ref_wm_seg)
                dice = dice_output[-9:]
                os.chdir('..')

                dice_sum += float(dice)
                n_subject += 1
                dice_file.write(subject_dir + ': ' + dice)

                # Error map
                if first:
                    error_map_sum = np.zeros(ref_wm_seg_im.data[0].shape)
                    error_map_abs_sum = np.zeros(ref_wm_seg_im.data[0].shape)
                    first = False

                error_3d = (ref_wm_seg_im.data - res_im.data) + 1
                error_3d_abs = abs(ref_wm_seg_im.data - res_im.data)

                error_map_sum += np.sum(error_3d, axis=0)
                error_map_abs_sum += np.sum(error_3d_abs, axis=0)

                n_slices += ref_wm_seg_im.data.shape[0]

                # Time of computation
                time_file.write(subject_dir + ' as target: ' + str(seg_time) + ' sec '
                                '- ' + str(seg_time / ref_wm_seg_im.data.shape[0]) + ' sec/target_slice\n')
                time_sum += seg_time

            except Exception, e:
                sct.printv('WARNING: an error occurred ...', 1, 'warning')
                print e
            # else:
            #    sct.run('rm -rf ' + tmp_dir)
    if e is None:
        dice_file.write('\nmean dice: ' + str(dice_sum/n_subject))
        dice_file.close()

        Image(param=(error_map_sum/n_slices) - 1, absolutepath='error_map.nii.gz').save()
        Image(param=error_map_abs_sum/n_slices, absolutepath='error_map_abs.nii.gz').save()

        time_file.write('\nmean computation time: ' + str(time_sum/n_subject) + ' sec')
        time_file.write('\nmean computation time per subject slice: ' + str(time_sum/n_slices) + ' sec')
        time_file.close()

if __name__ == "__main__":
        # Initialize the parser
        parser = Parser(__file__)
        parser.usage.set_description('Utility functions for the gray matter segmentation')
        parser.add_option(name="-crop",
                          type_value="folder",
                          description="Path to the folder containing all your subjects' data "
                                      "to be croped as pretreatment",
                          mandatory=False,
                          example='dictionary/')
        parser.add_option(name="-loocv",
                          type_value="folder",
                          description="Path to a dictionary folder to do 'Leave One Out Validation' on",
                          mandatory=False,
                          example='dictionary/')

        arguments = parser.parse(sys.argv[1:])

        if "-crop" in arguments:
            crop_t2_star(arguments['-crop'])
        if "-loocv" in arguments:
            leave_one_out(arguments['-loocv'])