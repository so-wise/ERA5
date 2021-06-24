%
% Basic plots
%

%% Initial setup

% clean up workspace
clear all 
close all

% add path
addpath ~/matlabfiles/
addpath ~/matlabfiles/m_map/

% colorbar
load('/users/dannes/colormaps/div11_RdBu.txt');
cmp = div11_RdBu./256;
load('/users/dannes/colormaps/cividis.txt');

% years to loop through
years = {'1992','1993','1994','1995','1996','1997','1998','1999','2000','2001',...
         '2002','2003','2004','2005','2006','2007','2008','2009','2010','2011',...
         '2012','2013','2014','2015','2016','2017','2018','2019','2020'};

% set variable names
variable_names = {'u10',...
                  'v10',...
                  'd2m',...
                  't2m',...
                  'e',...
                  'ro',...
                  'sp',...
                  'ssrd',...
                  'strd',...
                  'tp'};

% select file names
file_names = {'ERA5_sowise_u10m',...
              'ERA5_sowise_v10m',...
              'ERA5_sowise_dewpt2m',...
              'ERA5_sowise_tmp2m_degK',...
              'ERA5_sowise_evap',...
              'ERA5_sowise_runoff',...
              'ERA5_sowise_pres',...
              'ERA5_sowise_dsw',...
              'ERA5_sowise_dlw',...
              'ERA5_sowise_precip'};

%% Loop through data

for nvar=1:size(file_names,2)

    for nyear=1:1

        % file name and year
        file_name = file_names{nvar};
        variable_name = variable_names{nvar};
        year = years{nyear};

        disp(['Now plotting ' variable_name ' in year ' year])

        % load NetCDF
        name_nc = ['netcdf/' file_name '_' year '.nc'];  
        A_nc = ncread(name_nc, variable_name);
        x = ncread(name_nc,'longitude');
        y = ncread(name_nc,'latitude');
        t = ncread(name_nc,'time');
        nx = length(x); ny = length(y); nt = length(t);

        % grab units
        units = ncreadatt(name_nc, variable_name, 'units');
        long_var_name = ncreadatt(name_nc, variable_name, 'long_name');

        % grid
        [X,Y] = meshgrid(x,y);
        X = X'; Y = Y';

        % if last part is 'degK', replace with 'degC'
        %file_name = strrep(file_name, 'degK', 'degC'); 

        % load binary
        fid = fopen(['bin/' file_name '_' year],'r','ieee-be');
        A_bin = fread(fid,'float32');
        fclose(fid);

        % reshape
        A_bin = reshape(A_bin,[nx, ny, nt]);

        % plot first snapshot
        figPos = [440 143 838 633];
        figure('color','w','visible','off','position',figPos);
        m_proj('lambert','long',[-90 90],'lat',[-85 -28]);
        m_pcolor(X,Y,squeeze(A_bin(:,:,1)));
        shading flat;
        colorbar;

        % change colorbar 
        cmp_lin = (strcmp(variable_name,'tp')||...
                   strcmp(variable_name,'strd')||...
                   strcmp(variable_name,'ssrd')||...
                   strcmp(variable_name,'sp'));      
        if cmp_lin
          cmp_used = cividis;
        else
          cmp_used = flipud(cmp);
        end

        % if wind, set limit
        if strcmp(variable_name,'u10')||strcmp(variable_name,'v10')
          caxis([-15 15]);
        end

        % if pressure, set limit
        if strcmp(variable_name,'sp')
          caxis([9.5 10.5].*1e4);
        end

        % if needed, convert to rate
        isRate = strcmp(variable_name,'strd') || strcmp(variable_name,'ssrd') ||...
                 strcmp(variable_name,'e') || strcmp(variable_name,'tp') ||...
                 strcmp(variable_name,'ro');
        if isRate==1
          units = [units ' s**-1'];
        end

        % make plot
        colormap(cmp_used);
        m_coast('color',[1 .85 .7]);
        m_grid('box','fancy',...
               'tickdir','in',...
               'xtick',[-90 -60 -30 30 60],...
               'ytick',[-80 -60 -40],...
               'xaxislocation','top');
        title(['First snapshot of ' lower(long_var_name) ' (' units '), ' 'symbol: ' variable_name]);
        saveas(gcf,['plots/' file_name '_initial.jpg'],'jpg')

    end

end



