import xarray
import rioxarray
import geopandas
from shapely.geometry import mapping
import os, glob

# outdir
odir = '/home/adrian/NWP/S2S_Forecast/Trabajo_Mexico/data/c3s_regridded/pedro/ecmwf/outs'

# wdir
os.chdir('/home/adrian/NWP/S2S_Forecast/Trabajo_Mexico/data/c3s_regridded/pedro/ecmwf')

for ff in sorted(glob.glob('*.nc')):
    
    xds = xarray.open_dataset(ff)

    xds = xds[['tprate_ens_mean', 'tprate_ens_std']].transpose('step', 'lat', 'lon')

    xds.rio.set_spatial_dims(x_dim="lon", y_dim="lat", inplace=True)
    xds.rio.write_crs("EPSG:4326", inplace=True)
    geodf = geopandas.read_file("gadm36_CUB_0_sp.shp")

    clipped = xds.rio.clip(geodf.geometry.apply(mapping), geodf.crs).to_netcdf(odir+'/clipped_'+ff+'.nc')