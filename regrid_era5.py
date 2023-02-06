#
# Regrids ERA5 data onto MITgcm model data
#

# Import required packages
import scipy.interpolate as interpolate
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import MITgcmutils as mit
import xarray as xr
import numpy as np

# Load an ERA5 file
era5 = xr.open_dataset('netcdf_tmp/ERA5_sowise_u10m_1992.nc')

# Get the data for regridding
var = era5['u10'].values
lat = era5['latitude'].values
lon = era5['longitude'].values

# Get the model grid
model_X_grid = mit.mds.rdmds('../MITgcm/so-wise-gyre/grid/XC')[0,:] - 360
model_Y_grid = mit.mds.rdmds('../MITgcm/so-wise-gyre/grid/YC')[:,0]

# Create the lat-lon meshgrid
XX, YY = np.meshgrid(lon, lat)

# Create the target meshgrid
XX_target, YY_target = np.meshgrid(model_X_grid, model_Y_grid)

# Reshape the data for griddata
points = np.column_stack((XX.flatten(), YY.flatten()))
values = var[0,:,:].flatten()

# Interpolate the data to the target grid
regridded = interpolate.griddata(points, values, (XX_target, YY_target), method='linear')

# Plot the old field
fig = plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
pcm = ax.pcolormesh(lon, lat, var[0], transform=ccrs.PlateCarree())
plt.colorbar(pcm)
plt.title('Old Field')

# Plot the new field
fig = plt.figure(figsize=(15, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
pcm = ax.pcolormesh(model_X_grid, model_Y_grid, regridded, transform=ccrs.PlateCarree())
plt.colorbar(pcm)
plt.title('New Field')

plt.show()
