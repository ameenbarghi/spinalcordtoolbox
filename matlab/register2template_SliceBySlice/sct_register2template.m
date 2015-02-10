function sct_register2template(file_reg,file_src,levels)
% sct_register2template(file_reg,file_src,levels)
%-------------------------- FILES TO REGISTER -----------------------------------
% file_reg = {'data_highQ_mean_masked'}; % file to register
%--------------------------------------------------------------------------
%----------------------------OR--------------------------------------------
% file_src = 'data_highQ_mean_masked';
%--------------------------------------------------------------------------
% %-----------------------------REFERENCE (DESTINATION)------------------------------------
% ref_fname = '/Volumes/users_hd2/tanguy/data/Boston/2014-07/Connectome/template/PD_template.nii.gz';%'/home/django/tanguy/matlab/spinalcordtoolbox/data/template/MNI-Poly-AMU_WM.nii.gz';
% levels_fname='/home/django/tanguy/matlab/spinalcordtoolbox/data/template/MNI-Poly-AMU_level.nii.gz';
% %--------------------------------------------------------------------------

log='log_applytransfo';
% levels=5:-1:2;
warp_transfo = 1;

%-------------------------- FILES TO REGISTER -----------------------------------
% file_reg = {'data_highQ_mean_masked'}; % file to register
%--------------------------------------------------------------------------

%-----------------------------REFERENCE (DESTINATION)------------------------------------
ref_fname = '/Volumes/users_hd2/tanguy/data/Boston/2014-07/Connectome/template/diffusion_template.nii.gz';%'/home/django/tanguy/matlab/spinalcordtoolbox/data/template/MNI-Poly-AMU_WM.nii.gz';
levels_fname='/Volumes/hd2_local/users_local/tanguy/spinalcordtoolbox/data/template/MNI-Poly-AMU_level.nii.gz';
%--------------------------------------------------------------------------


%--------------------------SOURCE FILE--------------------------------------
% data = 'KS_HCP35_crop_eddy_moco_lpca'; 
% scheme = 'KS_HCP.scheme';
% % Generate good source image (White Matter image)
% if ~exist([data '_ordered.nii'])
%     opt.fname_log = log;
%     sct_dmri_OrderByBvals(data,scheme,opt)
% end
% scd_generateWM([data '_ordered'],scheme,log);
% param.maskname='mask_spinal_cord';
% if ~exist(param.maskname)
%     param.file = 'data_highQ_mean'; 
%     scd_GenerateMask(param);
% end
% if ~exist('data_highQ_mean_masked.nii'), unix(['fslmaths data_highQ_mean -mul ' param.maskname ' data_highQ_mean_masked']), end
% file_src = 'data_highQ_mean_masked';
%----------------------------OR--------------------------------------------
% file_src = 'data_highQ_mean_masked';
%--------------------------------------------------------------------------


%--------------------------------------------------------------------------
%---------------------------DON'T CHANGE BELOW-----------------------------
%--------------------------------------------------------------------------
%--------------------------------------------------------------------------

% read file_reg dim
[~,dim] = read_avw(file_reg{1});
[~,dim_ref] = read_avw(ref_fname);


% read template files
    % read levels
    levels_template=read_avw(levels_fname);
    z_lev=[];
    for i=levels
        [~,~,z]=find3d(levels_template==i); z_lev(end+1)=floor(mean(z));
    end
        
    % choose only good slices of the template
	template=load_nii(ref_fname);
    template_roi=template.img(:,:,z_lev);
    template_roi=make_nii(double(template_roi),[0.5 0.5 0.5],[],[]);
    save_nii(template_roi,'template_roi.nii')
    ref_fname = 'template_roi';

%     % apply sqrt
%     unix('fslmaths template_roi -sqrt -sqrt template_roi_sqrt');
%     ref_fname = 'template_roi_sqrt';
    
files_ref = sct_sliceandrename(ref_fname, 'z');

% splitZ source
files_src = sct_sliceandrename(file_src, 'z');

%--------------------------------------------------------------------------
% Estimate transfo between source and GW template
%--------------------------------------------------------------------------

for level = 1:dim(3)
    cmd = ['ants 2 -m CC[' files_ref{level} ',' files_src{level} ',1,4] -t SyN -r Gauss[3,1] -o reg_ -i 1x50 --number-of-affine-iterations 1000x1000x1000 --rigid-affine true --ignore-void-origin true -r 0'];
    j_disp(log,['>> ',cmd]); [status result] = unix(cmd);
    
     % copy and rename matrix
     mat_folder{level} = ['mat_level' num2str(level)];
     if ~exist(mat_folder{level},'dir'), mkdir(mat_folder{level}); end
     unix(['mv reg_Warp.nii.gz ' mat_folder{level} '/reg_Warp.nii.gz']);
     unix(['mv reg_InverseWarp.nii.gz ' mat_folder{level} '/reg_InverseWarp.nii.gz']);
     unix(['mv reg_Affine.txt ' mat_folder{level} '/reg_Affine.txt']);
     unix(['rm ' files_src{level}]);

end




%--------------------------------------------------------------------------
% apply transfo
%--------------------------------------------------------------------------

for i_file_reg = 1:length(file_reg)
files_reg = sct_sliceandrename(file_reg{i_file_reg}, 'z');
for level = 1:dim(3)
    if warp_transfo, warp_mat = [mat_folder{level} '/reg_Warp.nii.gz ']; else warp_mat = ' '; end
    % split
    files_tmp = sct_sliceandrename(files_reg{level}, 't');
    for iT=1:dim(4)
        % register reg file
        cmd = ['WarpImageMultiTransform 2 ' files_tmp{iT} ' ' files_tmp{iT} '_reg.nii.gz  -R ' files_ref{level} ' ' warp_mat  mat_folder{level} '/reg_Affine.txt --use-BSpline'];
        j_disp(log,['>> ',cmd]); [status result] = unix(cmd); if status, error(result); end
    end
    
    cmd = ['fslmerge -t ' sct_tool_remove_extension(files_reg{level},0) '_reg.nii.gz ' sct_tool_remove_extension(file_reg{i_file_reg},1) '*t*_reg*'];
    j_disp(log,['>> ',cmd]); [status result] = unix(cmd); if status, error(result); end
    unix(['rm ' sct_tool_remove_extension(file_reg{i_file_reg},1) '*t*']);
    unix(['rm ' files_reg{level}]);
end

% merge files
%reg
mergelist='';
for iZ=1:dim(3)
    mergelist=[mergelist sct_tool_remove_extension(files_reg{iZ},0) '_reg '];
end
cmd = ['fslmerge -z ' sct_tool_remove_extension(file_reg{i_file_reg},1) '_reg ' mergelist];
j_disp(log,['>> ',cmd]); [status result] = unix(cmd); if status, error(result); end
unix(['rm ' sct_tool_remove_extension(file_reg{i_file_reg},0) '_z*_reg*']);


end

% remove matrix
unix('rm -rf mat_level*');
% remove template
for level = 1:dim(3), delete([files_ref{level} '*']); end
%delete([ref_fname '*']);
% display
unix('fslview template_roi data_highQ_mean_masked_reg')