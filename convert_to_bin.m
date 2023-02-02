%
% Convert NetCDF to binary
%

% clean up workspace
clear all
close all
clear memory

% directory structure
fin_root_dir = 'netcdf/';
fout_root_dir = 'bin/';

% time covered by each file (6h)
dt = 21600.0;

% convert from dewpoint temp. to specific humidity
dt2aqh = 1.0;

% years to loop through
%years = {'1992','1993','1994','1995','1996','1997','1998','1999','2000','2001',...
%         '2002','2003','2004','2005','2006','2007','2008','2009','2010','2011',...
%         '2012','2013','2014','2015','2016','2017','2018','2019','2020'};
years = {'1992'};

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

% error check
if length(file_names)~=length(variable_names) 
    error('List of file names must have same length as list of variable names')
end

% loop through years
for nf=1:length(file_names) 

    for ny=1:length(years)

        % get file, variable, and year
        file = file_names{nf};
        variable = variable_names{nf};
        year = years{ny};

        % full file name
        file_in_name = [fin_root_dir file '_' year '.nc'];
        file_out_name = [fout_root_dir file '_issue01_' year];

        % progress message
        disp(['Now converting: ' file_in_name])

        % read netCDF
        lon = ncread(file_in_name,'longitude');
        lat = ncread(file_in_name,'latitude');
        time = ncread(file_in_name,'time');
        myVar0 = ncread(file_in_name,variable);

        % convert from dewpoint temp. to specific humidity
        %if strcmp(variable,'d2m')
        %    myVar0 = myVar0.*dt2aqh;
        %end

        % if needed, convert to rate
        isRate = strcmp(variable,'strd') || strcmp(variable,'ssrd') ||...
                 strcmp(variable,'e') || strcmp(variable,'tp') ||...
                 strcmp(variable,'ro');
        % convert
        if isRate==1 
            % convert from integrated value to rate
            myVar0 = myVar0./dt; 
        end

        % if the field is temperature, change to degC
        %if strcmp(variable,'t2m')
        %  myVar0 = myVar0 - 273.15;
        %  file_out_name = strrep(file_out_name,'degK','degC');
        %end

        % get sizes
        nx = length(lon); ny = length(lat); nt = length(time); 
        disp('---- nx, ny, nt ----')
        disp(nx), disp(ny), disp(nt)
        disp('--- min(x), min(y) ---')
        disp(min(lon)), disp(min(lat))

        % reshaping [assumes (x,y,t) structure]
        [x, y] = meshgrid(lon, lat);
        x = x'; y = y';
        myVar0 = flip(myVar0,2);  % flipping required for MITgcm convention
        myVar1D = reshape(myVar0, [nx*ny*nt,1]);

        % write to binary
        fid = fopen(file_out_name,'w','ieee-be');
        fwrite(fid,myVar1D,'float32');
        fclose(fid);

        % read it back in to check it
        fid = fopen(file_out_name,'r','ieee-be');
        A = fread(fid,'float32');
        A = reshape(A,[nx, ny, nt]);

        % basic checking
        format long
        disp('-- Mean of field before and after writing to binary')
        disp(nanmean(myVar1D(:)))
        disp(nanmean(A(:)))
        
    end

end


