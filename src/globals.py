from netCDF4 import Dataset

dataset         = None        # netcdf data structure
fields_toolbar  = None        # toolbar for selecting scalar and vector fields
time_toolbar    = None        # toolbar for changing/animating time index
lut             = None        # color lookup table
globe           = None        # spherical representation of planet
map             = None        # flat representation of planet
time_index      = 0           # current netcdf file time index
sfield_index    = 0           # currently selected scalar field index
level_index     = 0           # current vertical level index