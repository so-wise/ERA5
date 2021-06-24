#
# Driver: get ERA5 fields
#

import era5_helper as era5

#
# select format ('grib' or 'netcdf')
#
file_format = 'netcdf'

# set 
if file_format=='netcdf':
  file_root_dir = 'netcdf/'
elif file_format=='grib':
  file_root_dir = 'grib/'
else:
  print('ERA5: Format must be either grib or netcdf')

# define variable names to be downloaded
variable_names = ['10m_u_component_of_wind', 
                  '10m_v_component_of_wind', 
                  '2m_dewpoint_temperature',
                  '2m_temperature', 
                  'evaporation', 
                  'runoff',
                  'surface_pressure', 
                  'surface_solar_radiation_downwards', 
                  'surface_thermal_radiation_downwards',
                  'total_precipitation']

# select file names
file_names = ['ERA5_sowise_u10m',
              'ERA5_sowise_v10m',
              'ERA5_sowise_dewpt2m',
              'ERA5_sowise_tmp2m_degK',
              'ERA5_sowise_evap',
              'ERA5_sowise_runoff',
              'ERA5_sowise_pres',
              'ERA5_sowise_dsw',
              'ERA5_sowise_dlw',
              'ERA5_sowise_precip']

# add the root 
file_names = [file_root_dir + s for s in file_names]

# select years to download
years = ['1992','1993','1994','1995','1996','1997','1998','1999','2000','2001',
         '2002','2003','2004','2005','2006','2007','2008','2009','2010','2011',
         '2012','2013','2014','2015','2016','2017','2018','2019','2020']

#
# -- loop over variables and years to download individual files
#
for variable_name, file_name in zip(variable_names, file_names):
    for year in years:

        # show which request we're now making
        print('Now acquiring field: ',variable_name,'\n', 
              'Local filename: ',file_name,'\n',
              'Year: ',year,'\n',
              'Format: ',file_format)

        # call function to make the API request 
        era5.get_field(variable_name, 
                       year,
                       file_name + '_' + year, 
                       file_format=file_format)

#
