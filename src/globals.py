from netCDF4 import Dataset

dataset         = None        # netcdf data structure
fields_toolbar  = None        # toolbar for selecting scalar and vector fields
time_toolbar    = None        # toolbar for changing/animating time index
lut             = None        # color lookup table
quadsphere      = None        # surface made of quadrilaters in spherical coords
time_index      = 0
sfield_index    = 0           # currently selected scalar field