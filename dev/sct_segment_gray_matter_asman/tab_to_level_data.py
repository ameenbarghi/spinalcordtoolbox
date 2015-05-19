#!/usr/bin/env python
'''
dice_file = open('./dice_coeffs.txt', 'r')
data_lines = dice_file.readline().split('\r')
dice_file.close()

seg_type = data_lines[0].split('\t')
reg = data_lines[1].split('\t')
use_levels = data_lines[2].split('\t')
model_type = data_lines[3].split('\t')

case1_dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}
case2_dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}
case3_dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}
case4_dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}
case5_dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}
case6_dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}


for slice_line in data_lines[4:]:
    slice_line = slice_line.split('\t')

    level = slice_line[2]
    case1_dic[level].append(slice_line[3])
    case2_dic[level].append(slice_line[4])
    case3_dic[level].append(slice_line[5])
    case4_dic[level].append(slice_line[6])
    case5_dic[level].append(slice_line[7])
    case6_dic[level].append(slice_line[8])


data_by_level = open('data_by_level.txt', 'w')

data_by_level.write('WM SEG - RIGID_AFFINE - NO LEVELS - MODEL WM\n')
for level in case1_dic.keys():
    s_dices = ''
    for dice in case1_dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')


data_by_level.write('WM SEG - RIGID_AFFINE - WITH LEVELS - MODEL WM\n')
for level in case2_dic.keys():
    s_dices = ''
    for dice in case2_dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')


data_by_level.write('WM SEG - AFFINE - NO LEVELS - MODEL WM\n')
for level in case3_dic.keys():
    s_dices = ''
    for dice in case3_dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')


data_by_level.write('WM SEG - AFFINE - WITH LEVELS - MODEL WM\n')
for level in case4_dic.keys():
    s_dices = ''
    for dice in case4_dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')


data_by_level.write('GM SEG - AFFINE - WITH LEVELS - MODEL GM\n')
for level in case5_dic.keys():
    s_dices = ''
    for dice in case5_dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')


data_by_level.write('GM SEG - AFFINE - WITH LEVELS - MODEL WM\n')
for level in case6_dic.keys():
    s_dices = ''
    for dice in case6_dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')

data_by_level.close()
'''

dice_file = open('./dice_level.txt', 'r')
data_lines = dice_file.readline().split('\r')
dice_file.close()


dic = {'C1': [], 'C2': [], 'C3': [], 'C4': [], 'C5': [], 'C6': [], 'C7': [], 'T1': [], 'T2': []}


for slice_line in data_lines:
    slice_line = slice_line.split('\t')

    level = slice_line[0]
    dic[level].append(slice_line[1])


data_by_level = open('data_by_level.txt', 'w')

data_by_level.write('GM SEG - AFFINE - NO LEVELS - MODEL WM\n')
for level in dic.keys():
    s_dices = ''
    for dice in dic[level]:
        s_dices += dice + ' , '
    data_by_level.write(level + ' : ' + s_dices[:-2] + '\n')
data_by_level.write('\n\n')


data_by_level.close()