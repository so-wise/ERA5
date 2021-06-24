#
# API for Copernicus Data Store
#
def get_field(variable_name, year, file_name, file_format='netcdf'):
# def get_field(variable_name, year, file_name, file_format=netcdf)
#
  # import this module (pip installed locally)
  import cdsapi

  # input checking : format
  if file_format=='netcdf':
    file_extension='.nc'
  elif file_format=='grib':
    file_extension='.bin'
  else:
    print('error: file format must be either netcdf or grib')

  # create instance of cdsapi.Client()
  c = cdsapi.Client()

  # call the retrieve function
  c.retrieve(
      'reanalysis-era5-single-levels',
      {
          'product_type': 'reanalysis',
          'variable': variable_name,
          'year': year,
          'month': [
              '01', '02', '03',
              '04', '05', '06',
              '07', '08', '09',
              '10', '11', '12',
          ],
          'day': [
              '01', '02', '03',
              '04', '05', '06',
              '07', '08', '09',
              '10', '11', '12',
              '13', '14', '15',
              '16', '17', '18',
              '19', '20', '21',
              '22', '23', '24',
              '25', '26', '27',
              '28', '29', '30',
              '31',
          ],
          'time': [
              '00:00', '06:00', '12:00',
              '18:00',
          ],
          'area': [
              -28, -90, -90, 
              90,
          ],
          'format': file_format,
      },
      file_name + file_extension)
#
#
# Helper function for read_binary and write_binary. 
# Given a precision (32 or 64) and endian-ness ('big' or 'little'), construct the python data type string.
#
def set_dtype (prec, endian):

    import sys

    if endian == 'big':
        dtype = '>'
    elif endian == 'little':
        dtype = '<'
    else:
        print('Error (set_dtype): invalid endianness')
        sys.exit()
    if prec == 32:
        dtype += 'f4'
    elif prec == 64:
        dtype += 'f8'
    else:
        print('Error (set_dtype): invalid precision')
        sys.exit()
    return dtype
#
# 
# Read an array from a binary file and reshape to the correct dimensions.

# Arguments:
# filename: path to binary file
# grid_sizes: list of length 2 or 3 containing [nx, ny] or [nx, ny, nz] grid sizes
# dimensions: string containing dimension characters ('x', 'y', 'z', 't') in any order, e.g. 'xyt'
# Optional keyword arguments:
# prec: precision of data: 32 (default) or 64
# endian: endian-ness of data: 'big' (default) or 'little'
def read_binary (filename, grid_sizes, dimensions, prec=32, endian='big'):

    import numpy as np
    import sys

    print(('Reading ' + filename))

    dtype = set_dtype(prec, endian)

    # Extract grid sizes
    nx = grid_sizes[0]
    ny = grid_sizes[1]
    if len(grid_sizes) == 3:
        # It's a 3D grid
        nz = grid_sizes[2]
    elif 'z' in dimensions:
        print(('Error (read_binary): ' + dimensions + ' is depth-dependent, but your grid sizes are 2D.'))
        sys.exit()

    # Read data
    data = np.fromfile(filename, dtype=dtype)

    # Expected shape of data
    shape = []
    # Expected size of data, not counting time
    size0 = 1
    # Now update these initial values
    if 'x' in dimensions:
        shape = [nx] + shape
        size0 *= nx
    if 'y' in dimensions:
        shape = [ny] + shape
        size0 *= ny
    if 'z' in dimensions:
        shape = [nz] + shape
        size0 *= nz

    if 't' in dimensions:
        # Time-dependent field; figure out how many timesteps
        if np.mod(data.size, size0) != 0:
            print('Error (read_binary): incorrect dimensions or precision')
            sys.exit()
        num_time = data.size//size0
        shape = [num_time] + shape
    else:
        # Time-independent field; just do error checking
        if data.size != size0:
            print('Error (read_binary): incorrect dimensions or precision')
            sys.exit()

    # Reshape the data and return
    return np.reshape(data, shape)            
        
#
# Write an array ("data"), of any dimension, to a binary file ("file_path"). 
# Optional keyword arguments ("prec" and "endian") are as in function read_binary.
#
def write_binary (data, file_path, prec=32, endian='big'):

    import numpy as np
    import sys

    print(('Writing ' + file_path))

    if isinstance(data, np.ma.MaskedArray):
        # Need to remove the mask
        data = data.data

    dtype = set_dtype(prec, endian)    
    # Make sure data is in the right precision
    data = data.astype(dtype)

    # Write to file
    id = open(file_path, 'w')
    data.tofile(id)
    id.close()

#
# to calculate specific humidity from pressure and temperature (coped from metpy)
#
# specific_humidity_from_dewpoint
def specific_humidity_from_dewpoint(pressure, dewpoint):
    """Calculate the specific humidity from the dewpoint temperature and pressure.

    Parameters
    ----------
    dewpoint:                
        Dewpoint temperature

    pressure:                 
        Pressure

    Returns
    -------
        Specific humidity


    See Also
    --------
    mixing_ratio, saturation_mixing_ratio

    """
    mixing_ratio = saturation_mixing_ratio(pressure, dewpoint)
    return specific_humidity_from_mixing_ratio(mixing_ratio)

# saturation mixing ratio(pressure, dewpoint)
def saturation_mixing_ratio(total_press, temperature):
    """Calculate the saturation mixing ratio of water vapor.

    This calculation is given total atmospheric pressure and air temperature.

    Parameters
    ----------
    total_press: 
        Total atmospheric pressure

    temperature: 
        Air temperature

    Returns
    -------
        Saturation mixing ratio, dimensionless

    Notes
    -----
    This function is a straightforward implementation of the equation given in many places,
    such as [Hobbs1977]_ pg.73:

    .. math:: r_s = \epsilon \frac{e_s}{p - e_s}


    """
    return mixing_ratio(saturation_vapor_pressure(temperature), total_press)

# specific humidity from mixing ratio 
def specific_humidity_from_mixing_ratio(mixing_ratio):
    """Calculate the specific humidity from the mixing ratio.

    Parameters
    ----------
    mixing_ratio: 
        Mixing ratio

    Returns
    -------
        Specific humidity

    Notes
    -----
    Formula from [Salby1996]_ pg. 118.

    .. math:: q = \frac{w}{1+w}

    * :math:`w` is mixing ratio
    * :math:`q` is the specific humidity

    See Also
    --------
    mixing_ratio, mixing_ratio_from_specific_humidity

    """
    return mixing_ratio / (1 + mixing_ratio)

# mixing ratio
def mixing_ratio(partial_press, total_press, molecular_weight_ratio=0.622):
    """Calculate the mixing ratio of a gas.

    This calculates mixing ratio given its partial pressure and the total pressure of
    the air. There are no required units for the input arrays, other than that
    they have the same units.

    Parameters
    ----------
    partial_press : `pint.Quantity`
        Partial pressure of the constituent gas

    total_press : `pint.Quantity`
        Total air pressure

    molecular_weight_ratio : `pint.Quantity` or float, optional
        The ratio of the molecular weight of the constituent gas to that assumed
        for air. Defaults to the ratio for water vapor to dry air
        (:math:`\epsilon\approx0.622`).

    Returns
    -------
        The (mass) mixing ratio, dimensionless (e.g. Kg/Kg or g/g)

    Notes
    -----
    This function is a straightforward implementation of the equation given in many places,
    such as [Hobbs1977]_ pg.73:

    .. math:: r = \epsilon \frac{e}{p - e}

    .. versionchanged:: 1.0
       Renamed ``part_press``, ``tot_press`` parameters to ``partial_press``, ``total_press``

    See Also
    --------
    saturation_mixing_ratio, vapor_pressure

    """
    return (molecular_weight_ratio * partial_press
            / (total_press - partial_press))

# saturation vapor pressure
def saturation_vapor_pressure(temperature):
    """Calculate the saturation water vapor (partial) pressure.

    Parameters
    ----------
    temperature : `pint.Quantity`
        Air temperature

    Returns
    -------
    `pint.Quantity`
        Saturation water vapor (partial) pressure

    See Also
    --------
    vapor_pressure, dewpoint

    Notes
    -----
    Instead of temperature, dewpoint may be used in order to calculate
    the actual (ambient) water vapor (partial) pressure.

    The formula used is that from [Bolton1980]_ for T in degrees Celsius:

    .. math:: 6.112 e^\frac{17.67T}{T + 243.5}

    """
    # Converted from original in terms of C to use kelvin. Using raw absolute values of C in
    # a formula plays havoc with units support.
    import numpy as np
    temperature = temperature - 273.15
    return 6.112 * np.exp(17.67 * temperature / (temperature + 243.5))
