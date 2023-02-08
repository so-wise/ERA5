
# Import modules
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import MITgcmutils as mit
from tqdm import tqdm
import xarray as xr
import numpy as np
import xesmf as xe
import os

# Data locations
fin  = 'netcdf_tmp/'
fout = 'bin_tmp/'

# List of all NetCDF files in the input directory
files = [f for f in os.listdir(fin) if f.endswith('.nc')]

#
# Input grid (ERA5)
#

# Load ERA5 dataset (just u10m for now, to calculate regridder)
ds = xr.open_dataset(fin + 'ERA5_sowise_u10m_1992.nc')

# Extract longitude and longitude, define input grid
XC_era = ds['longitude'].values
YC_era = ds['latitude'].values

# Define input grid
grid_in = {"lon": XC_era, 
           "lat": YC_era}

# Load data and convert to Dask array (each time snapshot is a block)
var = list(ds.data_vars.values())[0].values 

#
# Output grid (MITgcm SO-WISE configuration)
#

# Get the MITgcm model grid
XC_model = mit.mds.rdmds('../MITgcm/so-wise-gyre/grid/XC')[0,:] - 360 
YC_model = mit.mds.rdmds('../MITgcm/so-wise-gyre/grid/YC')[:,0]
XG_model = mit.mds.rdmds('../MITgcm/so-wise-gyre/grid/XG')[0,:] - 360 
YG_model = mit.mds.rdmds('../MITgcm/so-wise-gyre/grid/YG')[:,0]

# Define output grid
grid_out = {"lon": XC_model, 
            "lat": YC_model,
            "lon_b": XG_model,
            "lat_b": YG_model} 

#
# Regridder
#

# Calculate the regridding function (or load from existing weights)
regridder = xe.Regridder(grid_in, grid_out, "bilinear")
regridder

# Test the regridder out on an example slice
test_out = regridder(var[0,:,:])

# Initialise an array for the regridded output
var_out = np.empty((var.shape[0], test_out.shape[0], test_out.shape[1]))

# Loop over all NetCDF files in the input directory
for filename in files:

    # Display name of file that is being converted
    np.disp('Now working on:')
    np.disp(filename)

    # Open the NetCDF file
    ds = xr.open_dataset(os.path.join(fin, filename))

    # Get the plain numpy array
    var = list(ds.data_vars.values())[0].values

    # Loop over the time dimension, regrid each time slice
    for n in tqdm(range(var.shape[0])):

        # Apply regridder to each time slice
        var_out[n] = regridder(var[n])

    # Flip the latitude dimension to match MITgcm convention
    var_out = np.flip(var_out, 1)

    # Change from float64 to float32
    var_out = np.float32(var_out)

    # 

    # Write results to 32-bit binary file
    var_out.astype('>f4').flatten().tofile(os.path.join(fout, filename.replace('.nc', '')))
