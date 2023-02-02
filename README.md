# ERA5

This repository contains a collection of python and Matlab scripts to download and process ERA5 forcing fields from ECMWF. Below is a description of the repo:

- `plots/` : example plots to check the ERA5 forcing files
- `calculate_aqh.m` : calculates specific humidity from the ERA5 files (required for MITgcm)
- `calculate_trend.py` : calculate trend maps from the forcing data
- `convert_to_bin.m` : script that converts the NetCDF files to the binary format expected by MITgcm's EXF package
- `era5_helper.py` : helper functions for downloading ERA5 (specifies the limits of the SO-WISE domain)
- `main_get_era5.py` : as the name suggests, this is what actually downloads ERA5 from ECMWF
- `make_some_plots.m` : some simple plotting routines

The binary files produced using these scripts are given to MITgcm's EXF package as input. Below is an example temperature field plot:

![image](https://user-images.githubusercontent.com/11757453/216313214-8d2c9bcc-1f7b-4c71-8e35-837f9bc4c54d.png)

And one of downward longwave radiation:

![image](https://user-images.githubusercontent.com/11757453/216313791-441fb9b2-7f85-41eb-b52a-e29bf249c932.png)

See the `plots/` directory for a few more.
