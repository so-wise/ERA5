%
% calculate aqh (specific humidity)
%

%% Initial setup

% clean up workspace
clear all
close all
clear memory

% directory structure
nc_root_dir = 'netcdf/';
bin_root_dir = 'bin/';

% some coefficients
a1 = 611.2; a3 = 17.67; a4 = -243.5;
R_dry = 287.058; % J/kgK
R_vap = 461.0; % J/kgK
eps = R_dry./R_vap; 

% years to loop through
years = {'1992','1993','1994','1995','1996','1997','1998','1999','2000','2001',...
         '2002','2003','2004','2005','2006','2007','2008','2009','2010','2011',...
         '2012','2013','2014','2015','2016','2017','2018','2019','2020'};

%% Loop through data

% grid
lon = ncread('netcdf/ERA5_sowise_dewpt2m_1992.nc','longitude');
lat = ncread('netcdf/ERA5_sowise_dewpt2m_1992.nc','latitude');

%for nyear=1:size(years,2)
for nyear=1:size(years,2)

    % extract year
    year = years{nyear};

    % display progress
    disp(['Now processing year ' year]);

    % load data
    time = ncread([nc_root_dir 'ERA5_sowise_dewpt2m_' year '.nc'],'time');
    dewpoint_temp = ncread([nc_root_dir 'ERA5_sowise_dewpt2m_' year '.nc'],'d2m');
    pressure = ncread([nc_root_dir 'ERA5_sowise_pres_' year '.nc'],'sp');
    temp = ncread([nc_root_dir 'ERA5_sowise_tmp2m_degK_' year '.nc'],'t2m');

    % calculate saturation-specific humidity
    dewpoint_tempC = dewpoint_temp - 273.15;
    tempC = temp - 273.15;
    e_sat = a1.*exp(a3.*dewpoint_tempC./(dewpoint_tempC-a4));
    q_sat = eps.*e_sat./(pressure-((1-eps).*e_sat));

    % alternative form (NASA report)
    a = -4.9283; b = -2937.4; c = 23.5518; d = 273; 
    e_sx = 10.^(c+(b./(dewpoint_tempC+d))).*(dewpoint_tempC+d).^a;

    % write out to binary
    q_sat = flip(q_sat,2); % required for MITgcm convention
    A = reshape(q_sat,[size(q_sat,1)*size(q_sat,2)*size(q_sat,3) 1]);
    fid = fopen([bin_root_dir 'ERA5_sowise_spfh2m_' year],'w','ieee-be');
    fwrite(fid,A,'float32');
    fclose(fid); 

    % some stats
    disp(['--- min, mean, max : ', num2str(min(A(:))) ', ' num2str(mean(A(:))) ', ' num2str(max(A(:)))]) 

end

