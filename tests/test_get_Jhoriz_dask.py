import numpy as np
from pyamps import AMPS, get_J_horiz
from datetime import datetime
import apexpy

from pyamps.mlt_utils import mlt_to_mlon, mlon_to_mlt
from pyamps.plot_utils import equal_area_grid, Polarsubplot

from matplotlib import pyplot as plt
plt.ion()


v, By, Bz, tilt, f107 = 400, 0., -3., 0., 100.
h = 110.
epoch = 2020.
reft = datetime(int(epoch),3,23,12,0,0)
hemi = 'north' #or 'south'

amps = AMPS(v, By, Bz, tilt, f107, height=h)

# get grid
# mlats, mlts = amps.plotgrid_vector
mlats, mlts = map(lambda x: x.ravel(), amps.plotgrid_vector)
# mlats, mlts = map(lambda x: x.ravel(), amps.vectorgrid)
if hemi == 'south':
    mlats *= -1

# get grid in geographic coords
mlons = mlt_to_mlon(mlts, reft, epoch)
a = apexpy.Apex(epoch, refh = h)
# f1, f2, f3, g1, g2, g3, d1, d2, d3, e1, e2, e3 = a.basevectors_apex(glat, glon, height, coords  = 'geo')
glat, glon, error = a.apex2geo(mlats.flatten(),mlons,h)

# get j components from standard AMPS
je, jn = amps.get_total_current(mlat = mlats, mlt = mlts)
je_cf, jn_cf = amps.get_curl_free_current(mlat = mlats, mlt = mlts)
je_df, jn_df = amps.get_divergence_free_current(mlat = mlats, mlt = mlts)

# make inputs for get_J_horiz
inputs = amps.get_inputs()

blanks = np.ones(mlats.size)
heights, refts = h * blanks, np.tile(reft,blanks.size)
vs, Bys, Bzs, tilts, f107s = inputs['v']*blanks, inputs['By']*blanks, inputs['Bz']*blanks, inputs['tilt']*blanks, inputs['f107']*blanks


# blankv = np.ones(mlatv.size)
# heightv = height * blankv
# vv, Byv, Bzv, tiltv, f107v = inputs['v']*blankv, inputs['By']*blankv, inputs['Bz']*blankv, inputs['tilt']*blankv, inputs['f107']*blankv

# pray that get_J_horiz runs

chunksize = 15000
coords = 'apex'
Je, Jn = get_J_horiz(glat, glon, heights, refts, vs, Bys, Bzs, tilts, f107s, epoch = epoch, h_R = h, chunksize = chunksize, 
                     # coeff_fn = default_coeff_fn,
                     coords = coords,
                     kill_curlfree=False,
                     kill_divfree=False)

Je_cf, Jn_cf = get_J_horiz(glat, glon, heights, refts, vs, Bys, Bzs, tilts, f107s, epoch = epoch, h_R = h, chunksize = chunksize, 
                           # coeff_fn = default_coeff_fn,
                           coords = coords,
                           kill_curlfree=False,
                           kill_divfree=True)

Je_df, Jn_df = get_J_horiz(glat, glon, heights, refts, vs, Bys, Bzs, tilts, f107s, epoch = epoch, h_R = h, chunksize = chunksize, 
                           # coeff_fn = default_coeff_fn,
                           coords = coords,
                           kill_curlfree=True,
                           kill_divfree=False)

if hemi == 'south':
    jn, jn_cf, jn_df, Jn, Jn_cf, Jn_df = map(lambda x: -1*x, [jn, jn_cf, jn_df, Jn, Jn_cf, Jn_df])

# Make plot for comparison
# get the grids:

# set up figure and polar coordinate plots:
fig = plt.figure(figsize = (15, 15))

showhemis = [hemi]
ncol = 16*len(showhemis)
for ih,hemi in enumerate(showhemis):

    pax_amps    = Polarsubplot(plt.subplot2grid((3, ncol), (0,  ih*ncol  ), colspan = 8), minlat = amps.minlat, linestyle = ':', linewidth = .3, color = 'lightgrey')
    pax_getj    = Polarsubplot(plt.subplot2grid((3, ncol), (0,  ih*ncol+8), colspan = 8), minlat = amps.minlat, linestyle = ':', linewidth = .3, color = 'lightgrey')
    pax_amps_cf = Polarsubplot(plt.subplot2grid((3, ncol), (1,  ih*ncol  ), colspan = 8), minlat = amps.minlat, linestyle = ':', linewidth = .3, color = 'lightgrey')
    pax_getj_cf = Polarsubplot(plt.subplot2grid((3, ncol), (1,  ih*ncol+8), colspan = 8), minlat = amps.minlat, linestyle = ':', linewidth = .3, color = 'lightgrey')
    pax_amps_df = Polarsubplot(plt.subplot2grid((3, ncol), (2,  ih*ncol  ), colspan = 8), minlat = amps.minlat, linestyle = ':', linewidth = .3, color = 'lightgrey')
    pax_getj_df = Polarsubplot(plt.subplot2grid((3, ncol), (2,  ih*ncol+8), colspan = 8), minlat = amps.minlat, linestyle = ':', linewidth = .3, color = 'lightgrey')
    # pax_c = plt.subplot2grid((1, ncol*10), (0, ncol*10-2), colspan = 2)
    
    # labels
    pax_amps.writeMLTlabels(mlat = amps.minlat, size = 14)
    pax_getj.writeMLTlabels(mlat = amps.minlat, size = 14)
    pax_amps.write(amps.minlat, 3,    str(amps.minlat) + r'$^\circ$' , ha = 'left', va = 'top', size = 14)
    pax_getj.write(amps.minlat, 3,    str(amps.minlat) + r'$^\circ$' , ha = 'left', va = 'top', size = 14)
    # pax_getj.write(amps.minlat, 3,    r'$-$' + str(amps.minlat) + '$^\circ$', ha = 'left', va = 'top', size = 14)
    pax_amps.write(amps.minlat-5, 12, r'AMPS methods' , ha = 'center', va = 'center', size = 18)
    pax_getj.write(amps.minlat-5, 12, r'get_J_horiz (dask)' , ha = 'center', va = 'center', size = 18)
    
    pax_amps.   write(amps.minlat-10, 18, r'Total'    , ha = 'center', va = 'center', size = 16, rotation=90)
    pax_amps_cf.write(amps.minlat-10, 18, r'Curl-free', ha = 'center', va = 'center', size = 16, rotation=90)
    pax_amps_df.write(amps.minlat-10, 18, r'Div-free' , ha = 'center', va = 'center', size = 16, rotation=90)

    vector_scale = 100
    ms = 5
    pax_amps.featherplot(np.abs(mlats), mlts, jn, je, SCALE = vector_scale, markersize = ms, unit = 'mA/m', linewidth = .5, color = 'gray', markercolor = 'grey')
    pax_getj.featherplot(np.abs(mlats), mlts, Jn, Je, SCALE = vector_scale, markersize = ms, unit = 'mA/m', linewidth = .5, color = 'gray', markercolor = 'grey')
    # pax_getj.featherplot(pmlatv, pmltv, ns, es, SCALE = vector_scale, markersize = ms, unit = None  , linewidth = .5, color = 'gray', markercolor = 'grey')
    
    pax_amps_cf.featherplot(np.abs(mlats), mlts, jn_cf, je_cf, SCALE = vector_scale, markersize = ms, unit = 'mA/m', linewidth = .5, color = 'gray', markercolor = 'grey')
    pax_getj_cf.featherplot(np.abs(mlats), mlts, Jn_cf, Je_cf, SCALE = vector_scale, markersize = ms, unit = 'mA/m', linewidth = .5, color = 'gray', markercolor = 'grey')
    
    pax_amps_df.featherplot(np.abs(mlats), mlts, jn_df, je_df, SCALE = vector_scale, markersize = ms, unit = 'mA/m', linewidth = .5, color = 'gray', markercolor = 'grey')
    pax_getj_df.featherplot(np.abs(mlats), mlts, Jn_df, Je_df, SCALE = vector_scale, markersize = ms, unit = 'mA/m', linewidth = .5, color = 'gray', markercolor = 'grey')
    
v = amps.inputs['v']
By = amps.inputs['By']
Bz = amps.inputs['Bz']
tilt = amps.inputs['tilt']
f107 = amps.inputs['f107']
strr = f'v     = {v:5.0f} km/s\nBy    = {By:5.2f} nT\nBz    = {Bz:5.2f} nT\ntilt  = {tilt:5.2f}°\nF10.7 = {f107:5.0f} sfu'

x = 0.02
y = 0.07
size = 12
ha = 'left'
descrip = fig.text(x,y, strr, ha=ha, size=size,fontdict={'family':'monospace'})
fig.suptitle(hemi.capitalize(),fontsize=20)
plt.tight_layout()
